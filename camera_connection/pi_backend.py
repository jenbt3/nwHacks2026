from fastapi import FastAPI
from fastapi.responses import StreamingResponse, HTMLResponse
import cv2
import uvicorn

app = FastAPI()

camera = cv2.VideoCapture(1)

if not camera.isOpened():
    print("Could not open camera")
    exit()

def generate_frames():
    """Generator function to continuously capture and yield frames"""
    while True:
        ret, frame = camera.read()
        
        if not ret:
            print("Error reading frame")
            break
        
        # Encode frame as JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue
            
        frame_bytes = buffer.tobytes()
        
        # Yield frame in byte format for streaming
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.get('/video_feed')
async def video_feed():
    """Video streaming endpoint"""
    return StreamingResponse(
        generate_frames(),
        media_type='multipart/x-mixed-replace; boundary=frame'
    )

@app.get('/', response_class=HTMLResponse)
async def index():
    """Home page with embedded video stream"""
    return '''
    <html>
        <head>
            <title>Raspberry Pi Camera Stream</title>
        </head>
        <body>
            <h1>Live USB Camera Feed - FastAPI</h1>
            <img src="/video_feed" width="640" height="480">
        </body>
    </html>
    '''

if __name__ == '__main__':
    try:
        # Run on all network interfaces, accessible from other devices
        uvicorn.run(app, host='0.0.0.0', port=8000)
    finally:
        camera.release()
        cv2.destroyAllWindows()