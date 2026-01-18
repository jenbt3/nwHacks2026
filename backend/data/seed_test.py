import requests
import base64
import numpy as np
from deepface import DeepFace

# 1. Update this to your local or network IP
BACKEND_URL = "http://localhost:8000"
IMAGE_PATH = "test_face.jpg" 
NAME = "Sujal Kapoor"
RELATIONSHIP = "Lead Dev"
ANCHOR = "He is a 3rd-year CS student at McMaster."

def enroll_test_user():
    try:
        # Generate embedding
        results = DeepFace.represent(img_path=IMAGE_PATH, model_name="VGG-Face")
        
        # FIX: Ensure float32 precision matches the Pi's sync logic
        embedding = np.array(results[0]["embedding"], dtype=np.float32)

        # Convert to Base64 for Pydantic 'bytes' field
        encoding_b64 = base64.b64encode(embedding.tobytes()).decode('utf-8')

        payload = {
            "name": NAME,
            "relationship": RELATIONSHIP,
            "memory_anchor": ANCHOR,
            "encoding": encoding_b64
        }
        
        response = requests.post(f"{BACKEND_URL}/people/enroll", json=payload)
        
        if response.status_code == 200:
            print(f"✅ Success! Enrolled {NAME} with ID: {response.json()['id']}")
        else:
            print(f"❌ Error: {response.text}")

    except Exception as e:
        print(f"❌ Failed: {e}")

if __name__ == "__main__":
    enroll_test_user()