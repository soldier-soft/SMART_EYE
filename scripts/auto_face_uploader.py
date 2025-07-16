import os
import cv2
import face_recognition
import pickle
from pathlib import Path

DATABASE_PATH = os.path.abspath("core/face_recognition/face_encodings.pkl")
FACES_DIR = os.path.abspath("known_faces")

def load_existing_database():
    if os.path.exists(DATABASE_PATH):
        with open(DATABASE_PATH, 'rb') as f:
            return pickle.load(f)
    return []

def save_database(database):
    with open(DATABASE_PATH, 'wb') as f:
        pickle.dump(database, f)
    print(f"[INFO] Database updated with {len(database)} faces.")

def extract_name_from_filename(filename):
    # e.g., "elangovan_1.jpg" → "Elangovan"
    return Path(filename).stem.split('_')[0].capitalize()

def encode_faces_from_directory():
    database = load_existing_database()
    existing_paths = {entry['path'] for entry in database}
    added_count = 0

    for filename in os.listdir(FACES_DIR):
        filepath = os.path.join(FACES_DIR, filename)
        if filepath in existing_paths or not filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            continue

        try:
            image = face_recognition.load_image_file(filepath)
            encodings = face_recognition.face_encodings(image)

            if encodings:
                name = extract_name_from_filename(filename)
                database.append({
                    'name': name,
                    'encoding': encodings[0],
                    'path': filepath
                })
                added_count += 1
                print(f"[INFO] Added face: {name} from {filename}")
            else:
                print(f"[WARNING] No face found in {filename}")
        except Exception as e:
            print(f"[ERROR] Processing {filename}: {e}")

    save_database(database)
    print(f"[INFO] Auto Face Upload Complete. {added_count} new faces added.")

if __name__ == "__main__":
    encode_faces_from_directory()
