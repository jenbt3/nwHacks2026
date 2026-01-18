import cv2
import requests
import numpy as np
import base64
from deepface import DeepFace
from scipy.spatial.distance import cosine

BACKEND_URL = "http://localhost:8000"
MODEL_NAME = "Facenet512"

def load_knowledge_base():
    """Simulates the sync.py logic"""
    print("[Sync] Fetching knowledge base from backend...")
    try:
        response = requests.get(f"{BACKEND_URL}/people/sync", timeout=5)
        response.raise_for_status()
        visitors = response.json()
        
        kb = {}
        for v in visitors:
            # Decode the Base64 string from the backend
            raw_bytes = base64.b64decode(v['encoding'])
            # Reconstruct the float32 array
            encoding = np.frombuffer(raw_bytes, dtype=np.float32)
            kb[v['id']] = {"name": v['name'], "vec": encoding}
        
        print(f"[Sync] Loaded {len(kb)} identities.")
        return kb
    except Exception as e:
        print(f"❌ Sync Failed: {e}")
        return {}

def run_local_test():
    kb = load_knowledge_base()
    if not kb: return

    # Warm up DeepFace
    print("[Vision] Initializing Facenet512...")
    DeepFace.represent(np.zeros((224, 224, 3), dtype=np.uint8), model_name=MODEL_NAME, enforce_detection=False)

    cap = cv2.VideoCapture(1) # Use laptop webcam
    
    print("--- SYSTEM LIVE: PRESS 'Q' TO QUIT ---")
    
    while True:
        ret, frame = cap.read()
        if not ret: break

        # Use Haar Cascades (just like on the Pi) to find the face first
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)

        for (x, y, w, h) in faces:
            # Crop the face (ROI)
            face_roi = frame[y:y+h, x:x+w]
            
            try:
                # Extract vector from the crop
                results = DeepFace.represent(
                    face_roi, 
                    model_name=MODEL_NAME, 
                    detector_backend='skip', # Skip since we cropped manually
                    enforce_detection=False,
                    align=True
                )
                
                if results:
                    live_vec = np.array(results[0]["embedding"], dtype=np.float32)
                    
                    # Compare against KB
                    for vid, data in kb.items():
                        dist = cosine(live_vec, data['vec'])
                        
                        # Threshold 0.35 - 0.40 is usually good for VGG-Face
                        if dist < 0.45:
                            cv2.putText(frame, f"MATCH: {data['name']}", (x, y-10), 
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                            print(f"✅ Recognized {data['name']} (Dist: {dist:.4f})")
            except Exception as e:
                pass

        cv2.imshow('Cognitive Bridge Local Test', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_local_test()