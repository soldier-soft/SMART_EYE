import pyttsx3

class VoiceFeedback:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)

    def speak(self, message: str):
        print(f"Voice: {message}")
        self.engine.say(message)
        self.engine.runAndWait()
