import cv2
import requests
import time
import subprocess
import logging
import threading
from flask import Flask, Response
from vision.recogniser import identify_face, warm_up_model
from sync import load_knowledge_base

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BridgeNode")

# Global variables for cross-thread frame sharing
output_frame = None
lock = threading.Lock()

app = Flask(__name__)

# Configuration
BACKEND_URL = "http://YOUR_BACKEND_IP:8000"
EXIT_PROXIMITY_AREA = 50000 
DETECTION_DOWNSCALE = 0.25
FACE_MATCH_THRESHOLD = 0.35 

class BridgeEdgeNode:
    def __init__(self):
        self.knowledge_base = load_knowledge_base(BACKEND_URL)
        warm_up_model()
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.cap = cv2.VideoCapture(0)
        self.last_greeting_time = 0
        self.greeting_cooldown = 900 

    def process_vision(self):
        global output_frame, lock
        logger.info("[System] Vision Pipeline Started.")
        
        while True:
            ret, frame = self.cap.read()
            if not ret: break

            # 1. Update the global frame for the Dashboard stream
            with lock:
                output_frame = frame.copy()

            # 2. Local AI Processing (Downscaled for speed)
            small = cv2.resize(frame, (0, 0), fx=DETECTION_DOWNSCALE, fy=DETECTION_DOWNSCALE)
            gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)

            current_time = time.time()
            for (x, y, w, h) in faces:
                orig_x, orig_y = int(x / DETECTION_DOWNSCALE), int(y / DETECTION_DOWNSCALE)
                orig_w, orig_h = int(w / DETECTION_DOWNSCALE), int(h / DETECTION_DOWNSCALE)
                
                # Wandering Sentry Logic
                if (orig_w * orig_h) > EXIT_PROXIMITY_AREA:
                    self.trigger_wandering_alert()

                # Recognition Logic with Social Dignity Filter
                if current_time - self.last_greeting_time > self.greeting_cooldown:
                    face_roi = frame[orig_y:orig_y+orig_h, orig_x:orig_x+orig_w]
                    visitor = identify_face(face_roi, self.knowledge_base, threshold=FACE_MATCH_THRESHOLD)
                    
                    if visitor:
                        self.report_to_dashboard(visitor)
                        self.play_whisper(visitor['id'])
                        self.last_greeting_time = current_time

    def trigger_wandering_alert(self):
        try: requests.post(f"{BACKEND_URL}/alerts/wandering", timeout=0.2)
        except: pass

    def report_to_dashboard(self, visitor):
        try:
            payload = {"name": visitor['name'], "relation": visitor['relation']}
            requests.post(f"{BACKEND_URL}/alerts/detection", json=payload, timeout=0.5)
        except: pass

    def play_whisper(self, visitor_id):
        url = f"{BACKEND_URL}/scripts/generate/{visitor_id}"
        subprocess.Popen(["mpv", "--no-video", "--no-cache", "--cache-pause=no", url])

def gen_frames():
    """Generator for the MJPEG stream."""
    global output_frame, lock
    while True:
        with lock:
            if output_frame is None:
                continue
            # Encode frame as JPEG
            ret, buffer = cv2.imencode('.jpg', output_frame)
            frame_bytes = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        time.sleep(0.03) # Limit to ~25 FPS to save bandwidth

@app.route('/video_feed')
def video_feed():
    """Route that the Dashboard's <img> tag connects to."""
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    node = BridgeEdgeNode()
    
    # Start the Vision Pipeline in a background thread
    vision_thread = threading.Thread(target=node.process_vision)
    vision_thread.daemon = True
    vision_thread.start()

    # Start the Flask Web Server for the Dashboard
    # Host '0.0.0.0' allows other devices on the network to see the stream
    app.run(host='0.0.0.0', port=8000, threaded=True)