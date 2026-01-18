from deepface import DeepFace
from scipy.spatial.distance import cosine
import numpy as np

# model_name matches your existing recogniser.py choice
MODEL_NAME = "VGG-Face" 

def identify_face(frame, knowledge_base, threshold=0.40):
    """
    1. Runs DeepFace inference ONCE.
    2. Compares resulting vector against the local Knowledge Base via math.
    """
    try:
        # Extract embedding from live frame
        embeddings = DeepFace.represent(
            img_path=frame, 
            model_name=MODEL_NAME,
            enforce_detection=True,
            detector_backend="opencv"
        )
        
        if not embeddings:
            return None

        live_vec = embeddings[0]["embedding"]
        best_match = None
        min_dist = 1.0

        # High-speed vector math loop
        for visitor_id, stored_vec in knowledge_base.items():
            dist = cosine(live_vec, stored_vec)
            if dist < min_dist and dist < threshold:
                min_dist = dist
                best_match = visitor_id

        return best_match # Returns the integer ID for the /detect/{id} route

    except Exception:
        return None