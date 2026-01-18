import cv2
import requests
import time
import os
import subprocess
from vision.recogniser import identify_face, warm_up_model
from sync import load_knowledge_base

# Configuration (Ideally these should be imported from a shared constants file)
BACKEND_URL = "http://YOUR_BACKEND_IP:8000"
EXIT_PROXIMITY_AREA = 50000 
DETECTION_DOWNSCALE = 0.25
FACE_MATCH_THRESHOLD = 0.35

class BridgeEdgeNode:
    def __init__(self):
        print("[System] Initializing Cognitive Bridge...")
        self.knowledge_base = load_knowledge_base(BACKEND_URL)
        
        # Pre-load the 500MB VGG-Face model into RAM
        warm_up_model()
        
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        self.cap = cv2.VideoCapture(0)
        
        # Non-blocking cooldown state
        self.last_greeting_time = 0
        self.greeting_cooldown = 15  # seconds

    def run(self):
        while True:
            ret, frame = self.cap.read()
            if not ret: break

            # 1. Performance: Process a tiny frame for detection
            small = cv2.resize(frame, (0, 0), fx=DETECTION_DOWNSCALE, fy=DETECTION_DOWNSCALE)
            gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)

            current_time = time.time()

            for (x, y, w, h) in faces:
                # Scale coordinates back up to the original frame size
                orig_x, orig_y = int(x / DETECTION_DOWNSCALE), int(y / DETECTION_DOWNSCALE)
                orig_w, orig_h = int(w / DETECTION_DOWNSCALE), int(h / DETECTION_DOWNSCALE)
                
                # Check for Wandering (Always active, never blocked by sleep)
                if (orig_w * orig_h) > EXIT_PROXIMITY_AREA:
                    # Use a non-blocking background request for alerts
                    requests.post(f"{BACKEND_URL}/alerts/wandering", timeout=1)

                # 2. Context-Aware Recognition (Only if cooldown has passed)
                if current_time - self.last_greeting_time > self.greeting_cooldown:
                    # Extract the cropped face ROI to skip redundant detection
                    face_roi = frame[orig_y:orig_y+orig_h, orig_x:orig_x+orig_w]
                    
                    visitor_id = identify_face(
                        face_roi, 
                        self.knowledge_base, 
                        threshold=FACE_MATCH_THRESHOLD
                    )
                    
                    if visitor_id:
                        self.play_whisper(visitor_id)
                        self.last_greeting_time = current_time

    def play_whisper(self, visitor_id):
        try:
            response = requests.get(f"{BACKEND_URL}/scripts/generate/{visitor_id}", stream=True)
            if response.status_code == 200:
                with open("temp_whisper.mp3", "wb") as f:
                    for chunk in response.iter_content(chunk_size=1024):
                        f.write(chunk)
                
                # Play audio via mpv (non-blocking)
                subprocess.Popen(["mpv", "--no-video", "temp_whisper.mp3"]).wait()
                
                # Cleanup to prevent disk bloat
                if os.path.exists("temp_whisper.mp3"):
                    os.remove("temp_whisper.mp3")
        except Exception as e:
            print(f"[Audio] Error: {e}")

if __name__ == "__main__":
    node = BridgeEdgeNode()
    node.run()