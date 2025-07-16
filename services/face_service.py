import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import sqlite3
from core.face_recognition.face_recognizer import FaceRecognizer
from core.face_recognition.face_saver import FaceSaver
import cv2

class FaceService:
    def __init__(self, config: dict):
        self.config = config
        self.recognizer = FaceRecognizer(
            config['known_faces_dir'],
            config['db_path']
        )
        self.saver = FaceSaver(
            config['known_faces_dir'],
            config['db_path']
        )
    
    def recognize_faces(self, frame):
        """Recognize faces in frame"""
        return self.recognizer.recognize_faces(frame)
    
    def add_new_face(self, name: str):
        """Add new face to database"""
        return self.saver.capture_new_face(name)
    
    def get_known_faces(self):
        """Get list of known faces"""
        conn = sqlite3.connect(self.config['db_path'])
        c = conn.cursor()
        c.execute("SELECT name, image_path FROM faces")
        faces = c.fetchall()
        conn.close()
        return faces
    
    def update_face(self, old_name: str, new_name: str):
        """Update face name in database"""
        conn = sqlite3.connect(self.config['db_path'])
        c = conn.cursor()
        c.execute("UPDATE faces SET name = ? WHERE name = ?", (new_name, old_name))
        conn.commit()
        conn.close()
        self.recognizer._load_known_faces()