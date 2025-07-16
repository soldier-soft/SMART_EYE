import unittest
from core.hardware.arduino.arduino_comm import ArduinoComm

class TestArduinoInterface(unittest.TestCase):
    def setUp(self):
        self.arduino = ArduinoComm(port="/dev/ttyUSB0", baudrate=9600)

    def test_connect(self):
        connected = self.arduino.connect()
        self.assertTrue(connected)

    def test_send_command(self):
        self.arduino.connect()
        success = self.arduino.send_command("TEST_COMMAND")
        self.assertTrue(success)
        self.arduino.disconnect()

if __name__ == "__main__":
    unittest.main()
