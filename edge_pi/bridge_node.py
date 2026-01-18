# --- FULL bridge_node.py ---
import cv2
import requests
import time
import subprocess
import logging
import threading
import serial
from flask import Flask, Response, request
from vision.recogniser import identify_face, warm_up_model
from sync import load_knowledge_base

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BridgeNode")

output_frame = None
lock = threading.Lock()
app = Flask(__name__)

# CONFIG
BACKEND_URL = "http://10.19.132.171:8000"
EXIT_PROXIMITY_AREA = 50000 
DETECTION_DOWNSCALE = 0.25

# Arduino setup on Pi
try:
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=0)
except:
    ser = None
    logger.error("Arduino not found on /dev/ttyACM0")

class BridgeEdgeNode:
    def __init__(self):
        self.knowledge_base = load_knowledge_base(BACKEND_URL)
        warm_up_model()
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.cap = cv2.VideoCapture(0)
        self.last_greeting_time = 0

    def process_vision(self):
        global output_frame, lock
        while True:
            ret, frame = self.cap.read()
            if not ret: break
            with lock: output_frame = frame.copy()
            # ... Face detection logic ...

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/motor', methods=['POST'])
def motor_control():
    if not ser: return {"error": "No Arduino"}, 500
    data = request.json
    angle = data.get("direction", 0)
    force = data.get("distance", 0)
    
    direction = 'F' if (angle <= 90 or angle >= 270) else 'B'
    steps = int(force * 50)
    
    if steps > 5:
        ser.write(f"{direction},{steps}\n".encode())
    return {"status": "ok"}

def gen_frames():
    global output_frame, lock
    while True:
        with lock:
            if output_frame is None: continue
            ret, buffer = cv2.imencode('.jpg', output_frame)
            frame_bytes = buffer.tobytes()
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        time.sleep(0.04)

if __name__ == "__main__":
    node = BridgeEdgeNode()
    threading.Thread(target=node.process_vision, daemon=True).start()
    app.run(host='0.0.0.0', port=8000, threaded=True)