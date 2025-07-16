import sys
import os
import yaml
import argparse
import logging
import datetime
import requests

# Setup paths to import project modules (adjust '..' to your project root if needed)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.voice_interface.text_to_speech import TextToSpeech
from core.voice_interface.speech_to_text import SpeechToText
from services.vision_service import VisionService
from services.nav_service import NavigationService
from services.nav_service import NavService
from services.face_service import FaceService
from services.currency_service import CurrencyService
from scripts.auto_face_uploader import encode_faces_from_directory

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')


class ChatBot:
    def __init__(self, config_path='config/app_config.yaml'):
        parser = argparse.ArgumentParser(description="Smart Eye Chatbot")
        parser.add_argument('--config', type=str, default=config_path, help='Path to config file')
        args = parser.parse_args()
        config_path = args.config

        try:
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
                logging.info(f"Loaded configuration from {config_path}")
        except FileNotFoundError:
            logging.error(f"Config file not found: {config_path}")
            raise SystemExit(1)
        except yaml.YAMLError as e:
            logging.error(f"Error parsing YAML config: {e}")
            raise SystemExit(1)

        # Initialize core modules
        self.tts = TextToSpeech()
        self.stt = SpeechToText()
        self.vision = VisionService(self.config)

        # Optional services
        google_maps_key = self.config.get('api_keys', {}).get('google_maps')
        if google_maps_key:
            try:
                self.navigation = NavigationService(google_maps_key)
            except Exception as e:
                logging.error(f"NavigationService init failed: {e}")
                self.navigation = None
        else:
            logging.warning("Google Maps API key not found in config. Navigation service disabled.")
            self.navigation = None

        try:
            self.navigation = NavService(google_maps_key) if google_maps_key else None
        except Exception as e:
            logging.error(f"NavigationService init failed: {e}")
            self.navigation = None

        if not google_maps_key:
            logging.warning("Google Maps API key not found in config. Navigation disabled.")


        try:
            self.face = FaceService(self.config.get('face_recognition', {}))
        except Exception as e:
            logging.error(f"FaceService init failed: {e}")
            self.face = None

        try:
            self.currency = CurrencyService(self.config.get('currency_recognition', {}))
        except Exception as e:
            logging.error(f"CurrencyService init failed: {e}")
            self.currency = None

        self.running = False

    def greet(self):
        self.tts.speak("Hello! I'm your Smart Eye assistant. How can I help you today?")

    def get_date(self):
        today = datetime.datetime.now().strftime("%A, %d %B %Y")
        self.tts.speak(f"Today's date is {today}")

    def get_time(self):
        now = datetime.datetime.now().strftime("%H:%M:%S")
        self.tts.speak(f"The current time is {now}")

    def get_location(self):
        try:
            response = requests.get('https://ipinfo.io/json', timeout=5)
            data = response.json()
            city = data.get('city', 'Unknown city')
            region = data.get('region', 'Unknown region')
            country = data.get('country', 'Unknown country')
            loc = data.get('loc', 'Unknown coordinates')
            self.tts.speak(f"You are in {city}, {region}, {country}. Coordinates are {loc}.")
        except Exception as e:
            logging.error(f"Location retrieval failed: {e}")
            self.tts.speak("Sorry, I could not determine your location.")

    def wait_for_stop(self):
        """
        Wait for user commands in a submodule until 'stop' is said.
        """
        self.tts.speak("Say 'stop' to return to the main menu.")
        while True:
            try:
                command = self.stt.listen()
            except Exception as e:
                logging.error(f"Speech recognition error: {e}")
                self.tts.speak("Sorry, I didn't catch that. Please try again.")
                continue

            if command and 'stop' in command.lower():
                self.tts.speak("Stopping current operation and returning to main menu.")
                break
            else:
                yield command

    def handle_object_detection(self):
        self.tts.speak("Starting object detection.")
        for command in self.wait_for_stop():
            logging.info(f"Object detection processing: {command}")
            # Insert your object detection logic here
            self.tts.speak("Detecting objects...")

    def handle_face_recognition(self):
        if not self.face:
            self.tts.speak("Face recognition service is not available.")
            return

        self.tts.speak("Starting face recognition.")
        for command in self.wait_for_stop():
            logging.info(f"Face recognition processing: {command}")
            # Insert your face recognition logic here
            self.tts.speak("Recognizing faces...")

    def handle_add_face(self, command):
        if not self.face:
            self.tts.speak("Face recognition service is not available.")
            return

        name = command.lower().replace('add face', '').replace('new face', '').strip()
        if name:
            self.tts.speak(f"Adding new face for {name}. Please look at the camera.")
            try:
                # The FaceService class should have a method `add_new_face` which captures and stores the face
                self.face.add_new_face(name)
                self.tts.speak(f"Face for {name} added successfully.")
            except AttributeError:
                logging.error("FaceService object has no attribute 'add_new_face'")
                self.tts.speak("Face adding feature is not implemented yet.")
            except Exception as e:
                logging.error(f"Adding new face failed: {e}")
                self.tts.speak("Failed to add new face.")
        else:
            self.tts.speak("Please specify a name for the new face.")

    def handle_currency_recognition(self):
        if not self.currency:
            self.tts.speak("Currency detection service is not available.")
            return

        self.tts.speak("Starting currency recognition.")
        for command in self.wait_for_stop():
            logging.info(f"Currency recognition processing: {command}")
            # Insert your currency recognition logic here
            self.tts.speak("Recognizing currency...")

    def handle_navigation(self, command):
        if not self.navigation:
            self.tts.speak("Navigation service is not available.")
            return

        dest = command.lower().replace('navigate to', '').replace('route to', '').strip()
        if not dest:
            self.tts.speak("Please specify a destination.")
            return

        self.tts.speak(f"Finding route to {dest}.")
        try:
            route = self.navigation.get_route("current location", dest)
            # Assume your NavigationService has get_route() that returns route info,
            # and get_distance_duration() to parse it - if not, implement accordingly.

            if hasattr(self.navigation, 'get_distance_duration'):
                distance, duration = self.navigation.get_distance_duration(route)
                self.tts.speak(f"Route found. Distance: {distance}, Duration: {duration}.")
            else:
                # If method missing, just inform route found
                self.tts.speak("Route found. Unable to get distance and duration details.")
        except Exception as e:
            logging.error(f"Navigation failed: {e}")
            self.tts.speak("Failed to retrieve the route.")

    def handle_update_face_database(self):
        self.tts.speak("Uploading new face data from known faces folder.")
        try:
            encode_faces_from_directory()
            self.tts.speak("Face database has been updated.")
        except Exception as e:
            logging.error(f"Face database update failed: {e}")
            self.tts.speak("Failed to update face database.")

    def process_command(self, command):
        command = command.lower().strip()

        if 'object' in command and 'detect' in command:
            self.handle_object_detection()

        elif 'face' in command and 'recogn' in command:
            self.handle_face_recognition()

        elif 'add face' in command or 'new face' in command:
            self.handle_add_face(command)

        elif 'currency' in command and 'detect' in command:
            self.handle_currency_recognition()

        elif 'navigate' in command or 'route' in command:
            self.handle_navigation(command)

        elif 'update face database' in command:
            self.handle_update_face_database()

        elif 'date' in command:
            self.get_date()

        elif 'time' in command:
            self.get_time()

        elif 'location' in command:
            self.get_location()

        elif command in ['stop', 'exit', 'quit']:
            self.tts.speak("Goodbye!")
            self.running = False

        else:
            self.tts.speak("I didn't understand that command. Please try again.")

    def run(self):
        self.running = True
        self.greet()

        while self.running:
            self.tts.speak("Listening for your command.")
            try:
                command = self.stt.listen()
            except Exception as e:
                logging.error(f"Speech recognition error: {e}")
                self.tts.speak("An error occurred while listening. Please try again.")
                continue

            if command:
                self.process_command(command)
            else:
                self.tts.speak("Sorry, I didn't catch that. Please try again.")


if __name__ == '__main__':
    try:
        bot = ChatBot()
        bot.run()
    except KeyboardInterrupt:
        print("\n[INFO] Terminated by user.")
