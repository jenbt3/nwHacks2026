
from flask import Flask, Response
import cv2

app = Flask(__name__)


camera = cv2.VideoCapture(1)

if not camera.isOpened():
    raise RuntimeError("Could not open camera")

def get_frame():
    success, frame = camera.read()
    if not success:
        return None

    _, buffer = cv2.imencode(".jpg", frame)
    return buffer.tobytes()