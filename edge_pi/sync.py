import requests
import numpy as np
import base64
import logging

# Setup logging for field troubleshooting
logger = logging.getLogger("sync_service")

def load_knowledge_base(api_url):
    """
    Downloads all visitor profiles and reconstructs face vectors.
    Returns: { id: {"name": str, "relation": str, "vec": np.array} }
    """
    try:
        logger.info(f"[Sync] Fetching identities from {api_url}/people/sync...")
        response = requests.get(f"{api_url}/people/sync", timeout=10)
        response.raise_for_status()
        visitors = response.json()
        
        kb = {} 
        for v in visitors:
            try:
                # 1. Decode the Base64 string from the JSON response
                raw_bytes = base64.b64decode(v['encoding'])
                
                # 2. Reconstruct the float32 array (512-d for Facenet)
                encoding = np.frombuffer(raw_bytes, dtype=np.float32)
                
                # 3. Store full metadata for zero-latency lookups on the Pi
                kb[v['id']] = {
                    "name": v['name'],
                    "relation": v['relation'], # Matches updated backend field
                    "vec": encoding
                }
            except Exception as e:
                logger.error(f"[Sync] Failed to process visitor {v.get('id')}: {e}")
                continue
            
        logger.info(f"[Sync] Successfully synchronized {len(kb)} identities.")
        return kb

    except Exception as e:
        logger.critical(f"[Sync] Connection to backend failed: {e}")
        return {}