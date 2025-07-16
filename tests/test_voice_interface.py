import unittest
from unittest.mock import patch, MagicMock
from core.voice_interface.text_to_speech import TextToSpeech
from core.voice_interface.speech_to_text import SpeechToText

class TestTextToSpeech(unittest.TestCase):
    @patch('pyttsx3.init')
    def test_speech_initialization(self, mock_init):
        mock_engine = MagicMock()
        mock_init.return_value = mock_engine
        
        tts = TextToSpeech()
        mock_init.assert_called_once()
        mock_engine.setProperty.assert_any_call('rate', 150)

    @patch('pyttsx3.init')
    def test_async_speech(self, mock_init):
        mock_engine = MagicMock()
        mock_init.return_value = mock_engine
        
        tts = TextToSpeech()
        tts.speak("Test", async_mode=True)
        mock_engine.say.assert_called_with("Test")

class TestSpeechToText(unittest.TestCase):
    @patch('speech_recognition.Microphone')
    @patch('speech_recognition.Recognizer')
    def test_successful_listen(self, mock_recognizer, mock_mic):
        mock_audio = MagicMock()
        mock_recognizer.return_value.listen.return_value = mock_audio
        mock_recognizer.return_value.recognize_google.return_value = "test"
        
        stt = SpeechToText()
        result = stt.listen()
        self.assertEqual(result, "test")

    @patch('speech_recognition.Microphone')
    @patch('speech_recognition.Recognizer')
    def test_failed_listen(self, mock_recognizer, mock_mic):
        mock_recognizer.return_value.recognize_google.side_effect = Exception("Error")
        
        stt = SpeechToText()
        result = stt.listen()
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()