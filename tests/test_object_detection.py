import unittest
import cv2
import numpy as np
from core.object_detection.detector import ObjectDetector

class TestObjectDetection(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.detector = ObjectDetector(
            "data/models/yolov3.cfg",
            "data/models/yolov3.weights",
            "data/models/coco.names"
        )
    
    def test_detection(self):
        # Create a blank test image
        test_image = np.zeros((416, 416, 3), dtype=np.uint8)
        
        # Test detection
        processed, objects = self.detector.detect_objects(test_image)
        
        # Verify return types
        self.assertIsInstance(processed, np.ndarray)
        self.assertIsInstance(objects, list)
        
        # For a blank image, we might not detect anything
        # This test just verifies the function runs without error

if __name__ == '__main__':
    unittest.main()