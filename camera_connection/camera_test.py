import cv2

camera = cv2.VideoCapture(1)

if not camera.isOpened():
    print("could not open camera")
    exit()

print("live video - press 'q' to quit")

while True:
    ret, frame = camera.read()
    
    if not ret:
        print("error reading frame")
        break
    
    cv2.imshow('live Camera', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

camera.release()
cv2.destroyAllWindows()