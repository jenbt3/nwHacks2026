import requests
import numpy as np
import base64

def load_knowledge_base(api_url):
    """Syncs vectors from Backend using Base64 decoding."""
    try:
        response = requests.get(f"{api_url}/people/sync")
        visitors = response.json()
        
        kb = {}
        for v in visitors:
            # FIX: Use base64 instead of hex
            enc_bytes = base64.b64decode(v['encoding'])
            encoding = np.frombuffer(enc_bytes, dtype=np.float64)
            kb[v['id']] = encoding
        return kb
    except Exception as e:
        print(f"Sync failed: {e}")
        return {}