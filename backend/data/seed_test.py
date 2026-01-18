import requests
import base64
import numpy as np
from deepface import DeepFace

# Configuration
BACKEND_URL = "http://localhost:8000"
IMAGE_PATH = "test_face.jpg" # Ensure this file exists in your directory
NAME = "Sujal K"
RELATIONSHIP = "Lead Dev w beard"
ANCHOR = "He is a 3rd-year CS student at McMaster."

def enroll_test_user():
    try:
        print(f"Processing {IMAGE_PATH} with VGG-Face...")
        # 1. Generate embedding using the VGG-Face model
        results = DeepFace.represent(
            img_path=IMAGE_PATH, 
            model_name="Facenet512",
            detector_backend="opencv",
            enforce_detection=True
        )
        
        # 2. Ensure float32 precision for vector matching consistency
        embedding = np.array(results[0]["embedding"], dtype=np.float32)

        # 3. Convert to Base64 to satisfy Pydantic's bytes field
        encoding_b64 = base64.b64encode(embedding.tobytes()).decode('utf-8')

        payload = {
            "name": NAME,
            "relationship_type": RELATIONSHIP, # Updated to match models.py
            "memory_anchor": ANCHOR,
            "encoding": encoding_b64
        }
        
        print("Sending enrollment request to backend...")
        response = requests.post(f"{BACKEND_URL}/people/enroll", json=payload)
        
        if response.status_code == 200:
            print(f"✅ Success! Enrolled {NAME} with ID: {response.json()['id']}")
        else:
            print(f"❌ Backend Error: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"❌ Enrollment Failed: {e}")

if __name__ == "__main__":
    enroll_test_user()