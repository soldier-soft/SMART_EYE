from core.hardware.sensors.ultrasonic_sensor import UltrasonicSensor
from core.voice_interface.text_to_speech import speak
from core.hardware.arduino.serial_reader import read_distance

class SensorService:
    def __init__(self, threshold=100):
        self.sensor = UltrasonicSensor()
        self.threshold = threshold

    def describe_surroundings(self):
        distance = read_distance()
        if distance is not None:
            self.sensor.update_distance(distance)
            if self.sensor.is_obstacle_close(self.threshold):
                speak(f"Object detected at {distance:.2f} centimeters ahead.")
            else:
                speak("The path is clear.")
        else:
            speak("Sensor reading not available.")