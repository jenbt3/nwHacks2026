import requests
import base64
import numpy as np
from deepface import DeepFace

# Configuration
BACKEND_URL = "http://localhost:8000"
IMAGE_PATH = "test_face.jpg"  # Path to a clear photo of your face
NAME = "Sujal Kapoor"         # Using the user's name for the test
RELATIONSHIP = "Lead Dev"
ANCHOR = "He is working on the nwHacks 2026 project."

def enroll_test_user():
    # 1. Generate the 128-d vector (matching your recogniser.py model)
    print(f"Generating embedding for {IMAGE_PATH}...")
    results = DeepFace.represent(img_path=IMAGE_PATH, model_name="VGG-Face")
    embedding = np.array(results[0]["embedding"], dtype=np.float32)

    # 2. Convert vector to raw bytes for the database
    encoding_bytes = embedding.tobytes()
    # Convert bytes to base64 for the JSON request
    encoding_b64 = base64.b64encode(encoding_bytes).decode('utf-8')

    # 3. Hit the enrollment endpoint
    payload = {
        "name": NAME,
        "relationship": RELATIONSHIP,
        "memory_anchor": ANCHOR,
        "encoding": encoding_b64
    }
    
    response = requests.post(f"{BACKEND_URL}/people/enroll", json=payload)
    
    if response.status_code == 200:
        print("✅ Success! Visitor enrolled in bridge.db")
    else:
        print(f"❌ Failed: {response.text}")

if __name__ == "__main__":
    enroll_test_user()