import unittest
from core.navigation.gps.navigator import Navigator

class TestNavigation(unittest.TestCase):
    def setUp(self):
        self.navigator = Navigator(api_key="FAKE_API_KEY_FOR_TESTS")

    def test_init(self):
        self.assertIsNotNone(self.navigator)

    def test_get_route(self):
        # Mock method to avoid real API calls, but let's assume it returns a dict
        route = self.navigator.get_route("LocationA", "LocationB")
        self.assertIsInstance(route, dict)
        self.assertIn("distance", route)
        self.assertIn("duration", route)

    def test_navigation_voice_instructions(self):
        instructions = self.navigator.get_voice_instructions("LocationA", "LocationB")
        self.assertIsInstance(instructions, list)

if __name__ == "__main__":
    unittest.main()
