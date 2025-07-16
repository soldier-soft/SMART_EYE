from core.currency_recognition.currency_detector import CurrencyDetector
import cv2

class CurrencyService:
    def __init__(self, config: dict):
        self.detector = CurrencyDetector(
            config['model_path'],
            config['labels']
        )
    
    def detect_currency(self, frame):
        """Detect currency in frame"""
        return self.detector.detect_currency(frame)
    
    def get_currency_list(self):
        """Get list of supported currencies"""
        return self.detector.labels
    
    def validate_currency(self, image_path: str):
        """Validate currency from image file"""
        image = cv2.imread(image_path)
        if image is not None:
            return self.detect_currency(image)
        return None, 0.0