import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.object_detection.detector import ObjectDetector
from core.face_recognition.face_recognizer import FaceRecognizer
from core.currency_recognition.currency_detector import CurrencyDetector
import cv2
import random

class ObjectDetector:
    def __init__(self, config):
        self.config = config

    def detect_objects(self):
        # Simulated detection with label and distance in cm
        objects = [
            {'label': 'person', 'distance': random.randint(150, 300)},
            {'label': 'wall', 'distance': random.randint(100, 250)}
        ]
        return objects if random.choice([True, False]) else []
class VisionService:
    def __init__(self, config: dict):
        self.config = config
        self.object_detector = ObjectDetector(
            config['object_detection']['config_path'],
            config['object_detection']['weights_path'],
            config['object_detection']['classes_path']
        )
        self.face_recognizer = FaceRecognizer(
            config['face_recognition']['known_faces_dir'],
            config['face_recognition']['db_path']
        )
        self.currency_detector = CurrencyDetector(
            config['currency_recognition']['model_path'],
            config['currency_recognition']['labels']
        )
    
    def process_frame(self, frame, mode: str = "object"):
        """Process frame based on selected mode"""
        if mode == "object":
            return self.object_detector.detect_objects(frame)
        elif mode == "face":
            return self.face_recognizer.recognize_faces(frame)
        elif mode == "currency":
            return self.currency_detector.detect_currency(frame)
        else:
            return frame, []
    
    def get_camera_feed(self, mode: str = "object"):
        """Get live camera feed with processing"""
        cap = cv2.VideoCapture(0)
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            processed_frame, _ = self.process_frame(frame, mode)
            cv2.imshow(f'Vision Service - {mode.capitalize()} Mode', processed_frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
        cap.release()
        cv2.destroyAllWindows()