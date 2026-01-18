import requests
import numpy as np
import base64

def load_knowledge_base(api_url):
    try:
        response = requests.get(f"{api_url}/people/sync", timeout=10)
        response.raise_for_status()
        visitors = response.json()
        
        kb = {} 
        for v in visitors:
            # Decode the Base64 string provided by the FastAPI JSON response
            raw_bytes = base64.b64decode(v['encoding'])
            
            # Reconstruct the float32 array from the raw bytes
            encoding = np.frombuffer(raw_bytes, dtype=np.float32)
            kb[v['id']] = encoding
            
        print(f"[Sync] Successfully loaded {len(kb)} identities.")
        return kb
    except Exception as e:
        print(f"[Sync] Critical Error: {e}")
        return {}