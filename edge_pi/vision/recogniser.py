from deepface import DeepFace
from scipy.spatial.distance import cosine
import numpy as np

# Use 'VGG-Face' as per architecture
MODEL_NAME = "Facenet512" 

def warm_up_model():
    """Pre-loads the model into RAM to ensure <500ms inference on first run."""
    print("[Vision] Warming up Facenet512 model...")
    # A tiny black image to trigger the internal model load
    fake_img = np.zeros((224, 224, 3), dtype=np.uint8)
    try:
        DeepFace.represent(fake_img, model_name=MODEL_NAME, enforce_detection=False)
        print("[Vision] Model ready.")
    except Exception as e:
        print(f"[Vision] Warm-up failed: {e}")

def identify_face(face_roi, knowledge_base, threshold=0.35):
    """
    Receives a CROPPED face image to skip internal detection.
    Returns the visitor_id if a strong match is found.
    """
    try:
        # 1. Inference: Extract embedding from the already-cropped ROI
        # Using 'skip' prevents DeepFace from wasting CPU re-detecting the face
        results = DeepFace.represent(
            img_path=face_roi, 
            model_name=MODEL_NAME,
            enforce_detection=False,
            detector_backend="skip",
            align=True
        )
        
        if not results:
            return None

        live_vec = np.array(results[0]["embedding"], dtype=np.float32)
        best_match_id = None
        min_dist = threshold 

        # 2. Optimized Comparison
        for visitor_id, stored_vec in knowledge_base.items():
            # Check for shape mismatch to prevent runtime crashes
            if live_vec.shape != stored_vec.shape:
                continue
                
            dist = cosine(live_vec, stored_vec)
            
            if dist < min_dist:
                min_dist = dist
                best_match_id = visitor_id

        return best_match_id

    except Exception as e:
        print(f"[Vision] Recognition Error: {e}")
        return None