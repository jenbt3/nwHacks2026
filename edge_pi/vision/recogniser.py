from deepface import DeepFace
from scipy.spatial.distance import cosine
import numpy as np

# Use 'VGG-Face' as per your existing file
MODEL_NAME = "VGG-Face" 

def identify_face(frame, knowledge_base, threshold=0.35):
    """
    Returns the visitor_id if a strong match is found, otherwise returns None.
    Threshold lowered to 0.35 for stricter 'None' enforcement.
    """
    try:
        # 1. Inference: Extract live embedding
        results = DeepFace.represent(
            img_path=frame, 
            model_name=MODEL_NAME,
            enforce_detection=True,
            detector_backend="opencv"
        )
        
        if not results:
            return None

        live_vec = results[0]["embedding"]
        best_match_id = None
        # Start with 'threshold' as the max distance, so anything further is ignored
        min_dist = threshold 

        # 2. Optimized Comparison
        for visitor_id, embeddings in knowledge_base.items():
            # Support both single vectors and lists of vectors
            if not isinstance(embeddings, list):
                embeddings = [embeddings]
                
            for stored_vec in embeddings:
                dist = cosine(live_vec, stored_vec)
                
                # Only update if this person is CLOSER than the current best AND the threshold
                if dist < min_dist:
                    min_dist = dist
                    best_match_id = visitor_id

        # If no one was closer than 'threshold', best_match_id remains None
        return best_match_id

    except Exception:
        # Returns None if no face is detected or if an error occurs
        return None