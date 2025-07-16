import unittest
from unittest.mock import MagicMock
from core.voice_interface.command_handler import CommandHandler

class TestCommandHandler(unittest.TestCase):
    def setUp(self):
        self.mock_tts = MagicMock()
        self.mock_vision = MagicMock()
        self.mock_nav = MagicMock()
        self.handler = CommandHandler(self.mock_tts, self.mock_vision, self.mock_nav)
    
    def test_object_detection_command(self):
        self.handler.process_command("start object detection")
        self.mock_vision.get_camera_feed.assert_called_with('object')
    
    def test_navigation_command(self):
        self.mock_nav.get_route.return_value = {}
        self.mock_nav.get_distance_duration.return_value = ("1 km", "15 mins")
        self.handler.process_command("navigate to central park")
        self.mock_nav.get_route.assert_called_with("current location", "central park")

if __name__ == '__main__':
    unittest.main()