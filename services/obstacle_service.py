import logging
from core.hardware.arduino.serial_reader import read_distance
from core.voice_interface.text_to_speech import speak
from core.navigation.obstacle.path_suggester import PathSuggester

class ObstacleService:
    def __init__(self, threshold=50):
        self.active = False
        self.threshold = threshold
        self.suggester = PathSuggester()
        self.clear_count = 0
        logging.basicConfig(level=logging.CRITICAL)  # Suppress non-critical logs

    def activate(self):
        """Activate the obstacle detection system."""
        self.active = True
        speak("Obstacle detection activated.")

    def deactivate(self):
        """Deactivate the obstacle detection system."""
        self.active = False
        speak("Obstacle detection deactivated.")
        self.clear_count = 0

    def check_obstacles(self):
        """Check for obstacles and announce instructions only if detected."""
        if not self.active:
            return None

        try:
            distance = read_distance()
            if distance is None:
                return None

            if distance < self.threshold:
                direction = self.suggester.suggest_direction()
                speak(f"Obstacle detected ahead at {distance:.2f} centimeters.")
                speak(direction)
                self.clear_count = 0  # Reset count after obstacle
                return direction
            else:
                if self.clear_count < 3:
                    speak("Move forward. There is no obstacle.")
                    self.clear_count += 1
                return None

        except Exception as e:
            # Silently handle read errors without verbose output
            return None

    def execute_movement(self, command):
        """Simulate movement feedback based on voice command."""
        if not self.active:
            speak("Obstacle detection is off. Please activate it first.")
            return

        try:
            directions = {
                "forward": "Moving forward",
                "left": "Turning left",
                "right": "Turning right",
                "backward": "Moving backward"
            }

            response = directions.get(command.lower())
            if response:
                speak(response)
            else:
                speak("Unknown movement command.")
        except Exception:
            speak("Failed to execute movement.")
