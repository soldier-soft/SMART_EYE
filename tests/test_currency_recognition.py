import unittest
import numpy as np
from core.currency_recognition.currency_detector import CurrencyDetector

class TestCurrencyRecognition(unittest.TestCase):
    def setUp(self):
        # Mock model that always predicts the first class
        class MockModel:
            def predict(self, x):
                return np.array([[1.0, 0.0, 0.0]])  # Predicts first class with 100% confidence
        
        self.detector = CurrencyDetector(MockModel(), ["10", "20", "50"])
    
    def test_currency_detection(self):
        test_image = np.zeros((224, 224, 3), dtype=np.uint8)
        label, confidence = self.detector.detect_currency(test_image)
        self.assertEqual(label, "10")
        self.assertEqual(confidence, 1.0)

if __name__ == '__main__':
    unittest.main()