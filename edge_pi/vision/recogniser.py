from deepface import DeepFace
from scipy.spatial.distance import cosine
import numpy as np
import logging

# Setup local logging for Pi troubleshooting
logger = logging.getLogger("vision_recogniser")

# Switched to Facenet512 for superior 512-d vector precision
MODEL_NAME = "Facenet512" 

def warm_up_model():
    """Pre-loads Facenet512 into RAM to ensure sub-500ms inference later."""
    logger.info("[Vision] Warming up Facenet512 model...")
    # Standard Facenet input size is 160x160
    fake_img = np.zeros((160, 160, 3), dtype=np.uint8) 
    try:
        DeepFace.represent(fake_img, model_name=MODEL_NAME, enforce_detection=False)
        logger.info("[Vision] Model ready for inference.")
    except Exception as e:
        logger.error(f"[Vision] Warm-up failed: {e}")

def identify_face(face_roi, knowledge_base, threshold=0.35):
    """
    Compares a live face crop against the local knowledge base.
    knowledge_base: { id: {"name": str, "relation": str, "vec": np.array} }
    """
    try:
        # 1. Generate Embedding from the Pi's face crop
        # align=True helps with the patient's head tilt or movement
        results = DeepFace.represent(
            img_path=face_roi, 
            model_name=MODEL_NAME,
            enforce_detection=False,
            detector_backend="skip", # CRITICAL: Skip detection as ROI is already cropped
            align=True
        )
        
        if not results:
            return None

        live_vec = np.array(results[0]["embedding"], dtype=np.float32)
        best_match = None
        min_dist = threshold 

        # 2. Vector Matching Loop (O(1) lookups would require a Vector DB, 
        # but for small visitor sets, this loop is efficient enough)
        for visitor_id, data in knowledge_base.items():
            stored_vec = data["vec"]
            
            # Prevent crashes if vector dimensions don't match
            if live_vec.shape != stored_vec.shape:
                continue
            
            # Using Cosine Similarity as per technical specs
            dist = cosine(live_vec, stored_vec)
            
            if dist < min_dist:
                min_dist = dist
                best_match = {
                    "id": visitor_id,
                    "name": data["name"],
                    "relation": data["relation"]
                }

        if best_match:
            logger.info(f"[Vision] Match Found: {best_match['name']} (Dist: {min_dist:.4f})")
        
        return best_match

    except Exception as e:
        logger.error(f"[Vision] Recognition Error: {e}")
        return None