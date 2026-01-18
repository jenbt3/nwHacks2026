import cv2
import requests
import time
import subprocess
from recogniser import identify_face
from sync import load_knowledge_base

# Local Constants (Fixed paths for Pi)
BACKEND_URL = "http://YOUR_BACKEND_IP:8000"
EXIT_PROXIMITY_AREA = 50000 
DETECTION_DOWNSCALE = 0.25
FACE_MATCH_THRESHOLD = 0.40

class BridgeEdgeNode:
    def __init__(self):
        print("[System] Initializing Cognitive Bridge...")
        self.knowledge_base = load_knowledge_base(BACKEND_URL)
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.cap = cv2.VideoCapture(0)

    def run(self):
        while True:
            ret, frame = self.cap.read()
            if not ret: break

            small = cv2.resize(frame, (0, 0), fx=DETECTION_DOWNSCALE, fy=DETECTION_DOWNSCALE)
            gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)

            for (x, y, w, h) in faces:
                area = (w / DETECTION_DOWNSCALE) * (h / DETECTION_DOWNSCALE)
                
                # High-Priority Wandering Alert
                if area > EXIT_PROXIMITY_AREA:
                    requests.post(f"{BACKEND_URL}/alerts/wandering")

                # Context-Aware Recognition
                visitor_id = identify_face(frame, self.knowledge_base, threshold=FACE_MATCH_THRESHOLD)
                
                if visitor_id:
                    self.play_whisper(visitor_id)
                    time.sleep(15) # Cooldown for patient dignity

    def play_whisper(self, visitor_id):
        # Hits the centralized scripts route
        resp = requests.get(f"{BACKEND_URL}/scripts/generate/{visitor_id}", stream=True)
        if resp.status_code == 200:
            subprocess.run(["mpv", "--no-video", "-"], input=resp.content)

if __name__ == "__main__":
    node = BridgeEdgeNode()
    node.run()