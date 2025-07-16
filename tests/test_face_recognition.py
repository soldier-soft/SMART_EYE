import unittest
import cv2
import numpy as np
import os
from core.face_recognition.face_recognizer import FaceRecognizer
from core.face_recognition.face_saver import FaceSaver

class TestFaceRecognition(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create a temporary directory for testing
        os.makedirs("test_faces", exist_ok=True)
        cls.test_db = "test_face_db.db"
        
        # Create a test face image
        cls.test_image = np.zeros((100, 100, 3), dtype=np.uint8)
        cv2.imwrite("test_faces/test_face.jpg", cls.test_image)
    
    def test_face_saving(self):
        saver = FaceSaver("test_faces", self.test_db)
        result = saver.capture_new_face("Test Person")
        self.assertTrue(result)
        
        # Verify the face was added to the database
        recognizer = FaceRecognizer("test_faces", self.test_db)
        self.assertIn("Test Person", recognizer.known_face_names)
    
    @classmethod
    def tearDownClass(cls):
        # Clean up test files
        if os.path.exists(cls.test_db):
            os.remove(cls.test_db)
        if os.path.exists("test_faces"):
            for file in os.listdir("test_faces"):
                os.remove(os.path.join("test_faces", file))
            os.rmdir("test_faces")

if __name__ == '__main__':
    unittest.main()