# --- FULL bridge_node.py ---
import cv2
import requests
import time
import subprocess
import logging
import threading
import serial
import glob
from flask import Flask, Response, request
from vision.recogniser import identify_face, warm_up_model
from sync import load_knowledge_base

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BridgeNode")

output_frame = None
lock = threading.Lock()
app = Flask(__name__)

# CONFIG
BACKEND_URL = "http://10.19.132.171:8000"
EXIT_PROXIMITY_AREA = 50000 
DETECTION_DOWNSCALE = 0.25
FACE_MATCH_THRESHOLD = 0.35 

# --- DYNAMIC ARDUINO PORT SCANNER ---
def connect_arduino():
    """Scans for Arduino on ACM or USB ports."""
    potential_ports = glob.glob('/dev/ttyACM*') + glob.glob('/dev/ttyUSB*')
    for port in potential_ports:
        try:
            s = serial.Serial(port, 9600, timeout=0)
            logger.info(f"SUCCESS: Arduino discovered on {port}")
            return s
        except Exception as e:
            logger.warning(f"Skipping {port}: {e}")
    return None

# Global Serial Instance
ser = connect_arduino()

class BridgeEdgeNode:
    def __init__(self):
        # Initial sync and model prep
        self.knowledge_base = load_knowledge_base(BACKEND_URL)
        warm_up_model()
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.cap = cv2.VideoCapture(0)
        self.last_greeting_time = 0
        self.greeting_cooldown = 30 

    def process_vision(self):
        global output_frame, lock
        logger.info("[System] Vision Pipeline Started.")
        
        while True:
            ret, frame = self.cap.read()
            if not ret: 
                time.sleep(0.1)
                continue

            with lock:
                output_frame = frame.copy()

            # AI Processing
            small = cv2.resize(frame, (0, 0), fx=DETECTION_DOWNSCALE, fy=DETECTION_DOWNSCALE)
            gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)

            current_time = time.time()
            for (x, y, w, h) in faces:
                orig_x, orig_y = int(x / DETECTION_DOWNSCALE), int(y / DETECTION_DOWNSCALE)
                orig_w, orig_h = int(w / DETECTION_DOWNSCALE), int(h / DETECTION_DOWNSCALE)
                
                # Wandering Alert
                if (orig_w * orig_h) > EXIT_PROXIMITY_AREA:
                    self.trigger_wandering_alert()

                # Recognition Logic
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
        subprocess.Popen(["mpv", "--no-video", url])

def gen_frames():
    global output_frame, lock
    while True:
        with lock:
            if output_frame is None: continue
            ret, buffer = cv2.imencode('.jpg', output_frame)
            frame_bytes = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        time.sleep(0.04)

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/motor', methods=['POST'])
def motor_control():
    global ser  # Declared at the very start of the function to avoid SyntaxError
    
    if not ser: 
        ser = connect_arduino()
        if not ser: return {"error": "Arduino not connected"}, 500
    
    data = request.json
    angle = data.get("direction", 0)
    force = data.get("distance", 0)
    
    direction = 'F' if (angle <= 90 or angle >= 270) else 'B'
    steps = int(force * 50)
    
    if steps > 5:
        try:
            ser.write(f"{direction},{steps}\n".encode())
        except Exception as e:
            logger.error(f"Write failed: {e}")
            ser = None # Reset so next call tries to reconnect
            return {"error": "Serial communication lost"}, 500
            
    return {"status": "ok"}

if __name__ == "__main__":
    node = BridgeEdgeNode()
    
    # Start Vision Thread
    t = threading.Thread(target=node.process_vision)
    t.daemon = True
    t.start()

    # Start Flask Server
    app.run(host='0.0.0.0', port=8000, threaded=True)