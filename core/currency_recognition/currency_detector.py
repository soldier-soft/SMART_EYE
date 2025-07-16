import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
import time

class CurrencyDetector:
    def __init__(self, model_path, labels, confidence_threshold=0.5):
        try:
            self.model = load_model(model_path)
            print(f"[INFO] Model loaded from {model_path}")
        except Exception as e:
            print(f"[ERROR] Failed to load model: {e}")
            raise
        
        self.labels = labels
        self.confidence_threshold = confidence_threshold
        
        # Dynamically get expected input size from model input shape
        input_shape = self.model.input_shape  # e.g., (None, 100, 100, 3)
        if len(input_shape) == 4 and input_shape[3] == 3:
            self.input_size = (input_shape[1], input_shape[2])
            print(f"[INFO] Model expects input size: {self.input_size}")
        else:
            raise ValueError("[ERROR] Unexpected model input shape: " + str(input_shape))
    
    def preprocess_image(self, image):
        # Resize, convert BGR to RGB, normalize, expand dims for batch size
        try:
            image = cv2.resize(image, self.input_size)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image = image.astype('float32') / 255.0
            image = np.expand_dims(image, axis=0)
            return image
        except Exception as e:
            print(f"[ERROR] Preprocessing failed: {e}")
            return None
    
    def detect_currency(self, frame):
        processed = self.preprocess_image(frame)
        if processed is None:
            return "Error", 0.0
        
        try:
            predictions = self.model.predict(processed)
        except Exception as e:
            print(f"[ERROR] Prediction failed: {e}")
            return "Error", 0.0
        
        predicted_class = np.argmax(predictions[0])
        confidence = predictions[0][predicted_class]
        label = self.labels[predicted_class]
        
        # Only return label if confidence is above threshold
        if confidence < self.confidence_threshold:
            label = "Unknown"
        
        return label, confidence
    
    def detect_from_camera(self):
        cap = cv2.VideoCapture(0)
        prev_time = 0
        
        if not cap.isOpened():
            print("[ERROR] Cannot open camera")
            return
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("[ERROR] Failed to grab frame")
                break
            
            # Define detection region (center square)
            h, w = frame.shape[:2]
            detection_size = min(h, w) // 2
            x1 = w // 2 - detection_size // 2
            y1 = h // 2 - detection_size // 2
            x2 = x1 + detection_size
            y2 = y1 + detection_size
            
            detection_region = frame[y1:y2, x1:x2]
            
            label, confidence = self.detect_currency(detection_region)
            
            # Draw rectangle
            color = (0, 255, 0) if label != "Unknown" else (0, 0, 255)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            
            # Show label and confidence with background for readability
            text = f"{label}: {confidence:.2f}"
            (text_width, text_height), baseline = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
            cv2.rectangle(frame, (x1, y1 - text_height - baseline - 10), 
                                 (x1 + text_width, y1), color, -1)
            cv2.putText(frame, text, (x1, y1 - 5), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Calculate and show FPS
            curr_time = time.time()
            fps = 1 / (curr_time - prev_time) if prev_time else 0
            prev_time = curr_time
            cv2.putText(frame, f"FPS: {fps:.2f}", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            
            cv2.imshow('Currency Detection', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    labels = ['100 INR', '200 INR', '500 INR', '2000 INR']  # Adjust according to your model's classes
    model_path = "currency_model.h5"  # Change this path to your model file
    
    detector = CurrencyDetector(model_path, labels, confidence_threshold=0.6)
    detector.detect_from_camera()
