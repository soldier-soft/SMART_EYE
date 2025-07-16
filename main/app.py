import sys
import os
import yaml
import argparse
import logging
import threading
import time
from datetime import datetime
from pathlib import Path

# Add project root to system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import core modules
from core.object_detection.detector import ObjectDetector
from core.face_recognition.face_recognizer import FaceRecognizer
from core.face_recognition.face_saver import FaceSaver
from core.currency_recognition.currency_detector import CurrencyDetector
from core.navigation.gps.navigator import Navigator
from core.voice_interface.text_to_speech import TextToSpeech
from core.voice_interface.speech_to_text import SpeechToText
from core.hardware.sensors.sensor_manager import SensorManager
from services.obstacle_service import ObstacleService

# Configure logging
logging.basicConfig(level=logging.INFO)

# Get root and models path
project_root = Path(__file__).resolve().parents[1]
models_dir = project_root / "models"


class SmartEyeApp:
    def __init__(self, config_path):
        self.running = True
        self.config = self._load_config(config_path)
        self._initialize_components()

    def _load_config(self, config_path):
        """Load application config from YAML"""
        config_path = os.path.abspath(config_path)
        if not os.path.exists(config_path):
            logging.error(f"Config file not found: {config_path}")
            sys.exit(1)
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)

    def _initialize_components(self):
        """Initialize all module components from config"""
        try:
            yolo_cfg = self.config['object_detection']
            self.object_detector = ObjectDetector(
                yolo_cfg['config_path'],
                yolo_cfg['weights_path'],
                yolo_cfg['classes_path']
            )

            face_cfg = self.config['face_recognition']
            self.face_recognizer = FaceRecognizer(
                face_cfg['known_faces_dir'],
                face_cfg['db_path']
            )
            self.face_saver = FaceSaver(
                face_cfg['known_faces_dir'],
                face_cfg['db_path']
            )

            currency_cfg = self.config['currency_recognition']
            self.currency_detector = CurrencyDetector(
                currency_cfg['model_path'],
                currency_cfg['labels']
            )

            nav_cfg = self.config.get('navigation', {})
            self.navigator = Navigator(
                api_key=nav_cfg.get('google_maps_api_key'),
                gps_interval=nav_cfg.get('gps_update_interval', 5)
            )

            self.tts = TextToSpeech()
            self.stt = SpeechToText()

            obs_cfg = self.config.get('obstacle_avoidance', {})
            self.obstacle_service = ObstacleService(
                threshold=obs_cfg.get('alert_distance_cm', 30)
            )

            self.sensor_manager = SensorManager(
                port=obs_cfg.get('serial_port', 'COM11'),
                alert_distance=obs_cfg.get('alert_distance_cm', 30),
                alert_callback=self.obstacle_alert
            )

            self.obstacle_thread = None
            self.monitoring = False

        except Exception as e:
            logging.exception("Component initialization failed")
            sys.exit(1)

    def obstacle_alert(self, distance):
        logging.info(f"Obstacle detected at {distance} cm")
        self.tts.speak(f"Obstacle detected {distance} centimeters ahead.")
        suggestion = self.obstacle_service.check_obstacles()
        if suggestion:
            self.tts.speak(suggestion)

    def run_object_detection(self):
        try:
            self.tts.speak("Starting object detection.")
            self.object_detector.detect_from_camera()
        except Exception as e:
            logging.exception("Object detection failed")
            self.tts.speak("Object detection encountered an error.")

    def run_face_recognition(self):
        try:
            self.tts.speak("Starting face recognition.")
            self.face_recognizer.recognize_from_camera()
        except Exception as e:
            logging.exception("Face recognition failed")
            self.tts.speak("Face recognition encountered an error.")

    def add_new_face(self, name):
        if not name:
            self.tts.speak("Name cannot be empty.")
            return
        try:
            if self.face_saver.capture_new_faces(name):
                self.tts.speak(f"{name} added to face database.")
                self.face_recognizer._load_known_faces()
            else:
                self.tts.speak("Failed to add face.")
        except Exception as e:
            logging.exception("Failed to add new face")
            self.tts.speak("Error occurred while saving new face.")

    def run_currency_detection(self):
        try:
            self.tts.speak("Starting currency detection.")
            self.currency_detector.detect_from_camera()
        except Exception as e:
            logging.exception("Currency detection failed")
            self.tts.speak("Currency detection encountered an error.")

    def start_navigation(self):
        self.tts.speak("Please say your destination.")
        destination = self.stt.listen()
        if not destination:
            self.tts.speak("Destination not understood.")
            return
        if self.check_stop_command(destination):
            return
        try:
            self.navigator.navigate_to(destination)
            self.tts.speak(f"Navigating to {destination}.")
        except Exception as e:
            logging.exception("Navigation failed")
            self.tts.speak("Navigation failed.")

    def speak_current_location(self):
        try:
            self.navigator.speak_current_location()
        except Exception as e:
            logging.exception("Failed to get current location")
            self.tts.speak("Unable to determine current location.")

    def tell_time_and_date(self, command):
        now = datetime.now()
        if "time" in command:
            current_time = now.strftime("%I:%M %p")
            self.tts.speak(f"The current time is {current_time}.")
        elif "date" in command:
            current_date = now.strftime("%A, %B %d, %Y")
            self.tts.speak(f"Today is {current_date}.")

    def _obstacle_monitor_loop(self):
        try:
            self.sensor_manager.start_monitoring()
            self.obstacle_service.activate()
            self.tts.speak("Obstacle monitoring active.")
            while self.monitoring:
                time.sleep(1)
        except Exception as e:
            logging.exception("Obstacle monitoring failed")
            self.tts.speak("Error in obstacle monitoring.")
        finally:
            self.sensor_manager.stop_monitoring()
            self.obstacle_service.deactivate()
            logging.info("Obstacle monitoring stopped.")

    def start_obstacle_monitoring(self):
        if self.monitoring:
            self.tts.speak("Obstacle monitoring is already running.")
            return
        self.monitoring = True
        self.obstacle_thread = threading.Thread(target=self._obstacle_monitor_loop, daemon=True)
        self.obstacle_thread.start()

    def stop_obstacle_monitoring(self):
        if not self.monitoring:
            self.tts.speak("Obstacle monitoring is not active.")
            return
        self.monitoring = False
        if self.obstacle_thread:
            self.obstacle_thread.join(timeout=2)
        self.tts.speak("Obstacle monitoring stopped.")

    def process_command(self, command):
        command = command.lower()
        if 'stop' in command:
            self.tts.speak("Stopping current task.")
            return 'stop'
        elif 'object detection' in command:
            self.run_object_detection()
        elif 'face recognition' in command:
            self.run_face_recognition()
        elif 'add new face' in command:
            name = command.replace('add new face', '').strip()
            self.add_new_face(name)
        elif 'currency detection' in command:
            self.run_currency_detection()
        elif 'start navigation' in command:
            self.start_navigation()
        elif 'where is my location' in command:
            self.speak_current_location()
        elif 'time' in command or 'date' in command:
            self.tell_time_and_date(command)
        elif 'start obstacle' in command:
            self.start_obstacle_monitoring()
        elif 'stop obstacle' in command:
            self.stop_obstacle_monitoring()
        elif 'exit' in command or 'quit' in command:
            self.tts.speak("Goodbye!")
            self.running = False
        else:
            self.tts.speak("Command not recognized.")

    def check_stop_command(self, text=None):
        if not text:
            text = self.stt.listen()
        return text and 'stop' in text.lower()

    def voice_command_loop(self):
        self.tts.speak("Voice command mode activated. Say 'stop' to exit.")
        try:
            while self.running:
                command = self.stt.listen()
                if command and self.process_command(command) == 'stop':
                    break
        except Exception as e:
            logging.exception("Voice command error")
            self.tts.speak("Voice command failed.")

    def run(self):
        menu = """
--- Smart Eye Main Menu ---
1. Object Detection
2. Face Recognition
3. Add New Face
4. Currency Detection
5. Voice Command Mode
6. Start Navigation
7. obstacle_alert
8. Start Obstacle Monitoring
9. Stop Obstacle Monitoring
10. Exit
"""
        while self.running:
            print(menu)
            try:
                choice = input("Enter your choice (1-9): ").strip()
            except (EOFError, KeyboardInterrupt):
                self.tts.speak("Application exited.")
                break

            if choice == '1':
                self.run_object_detection()
            elif choice == '2':
                self.run_face_recognition()
            elif choice == '3':
                name = input("Enter name: ").strip()
                self.add_new_face(name)
            elif choice == '4':
                self.run_currency_detection()
            elif choice == '5':
                self.voice_command_loop()
            elif choice == '6':
                self.start_navigation()
            elif choice == '7':
                self.obstacle_alert(self)
            elif choice == '8':
                self.start_obstacle_monitoring()
            elif choice == '9':
                self.stop_obstacle_monitoring()
            elif choice == '10':
                self.tts.speak("Goodbye!")
                self.stop_obstacle_monitoring()
                self.running = False
            else:
                self.tts.speak("Invalid choice.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Smart Eye Application")
    parser.add_argument('--config', default='../config/app_config.yaml', help='Path to config YAML')
    args = parser.parse_args()

    app = SmartEyeApp(os.path.abspath(args.config))
    app.run()
