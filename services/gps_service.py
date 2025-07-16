from core.navigation.gps.location_finder import LocationFinder
from core.voice_interface.text_to_speech import speak

class GPSService:
    def __init__(self):
        self.locator = LocationFinder()

    def navigate(self, destination: str):
        speak(f"Navigating to {destination}")
        directions = self.get_directions(destination)
        for step in directions:
            speak(step)

    def get_location(self):
        location = self.locator.get_current_location()
        if location:
            speak(f"You are at latitude {location[0]} and longitude {location[1]}")
        else:
            speak("Unable to determine your location")
        return location

    def get_directions(self, destination: str):
        return [
            f"Head towards {destination}",
            "Turn right in 200 meters",
            "You have reached your destination"
        ]
