import cv2

def generate_frames():
    camera = cv2.VideoCapture(1)
    
    if not camera.isOpened():
        print("Could not open camera")
        return
    
    try:
        while True:
            ret, frame = camera.read()
            
            if not ret:
                print("Error reading frame")
                break
            
            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                continue
                
            frame_bytes = buffer.tobytes()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    
    finally:
        camera.release()