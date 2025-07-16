import unittest
from core.hardware.sensors.ultrasonic_sensor import UltrasonicSensor

class TestUltrasonicSensor(unittest.TestCase):
    def setUp(self):
        self.sensor = UltrasonicSensor(trigger_pin=23, echo_pin=24)

    def test_distance_measurement(self):
        distance = self.sensor.get_distance()
        self.assertIsInstance(distance, float)
        self.assertGreaterEqual(distance, 0.0)

if __name__ == "__main__":
    unittest.main()
