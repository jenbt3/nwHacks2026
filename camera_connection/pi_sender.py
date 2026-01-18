#feed the video feed from the raspberry pi camera to a server using sockets

import cv2
import socket
import pickle
import struct
import time

hostIP = '' # server IP
port = 0000 # server port

#connect to backend server
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((hostIP, port)) #change to your server ip and port

#setup camera; 0 is default camera
cam = cv2.VideoCapture(0)
cam.set(3, 640)
cam.set(4, 480)


try:
    while True:
        # capture a single frame from the camera
        ret, frame = cam.read()
        
        # serialize the frame (turn the image into a stream of 1s and 0s)
        data = pickle.dumps(frame)
        
        # pack the data and send it over the network
        message = struct.pack("Q", len(data)) + data
        client_socket.sendall(message)
        size = len(data)

        # Send the size of the frame first, then the frame itself
        client_socket.sendall(struct.pack(">L", size) + data)
        
        if cv2.waitKey(1) == ord('q'):
            break
finally:
    cam.release()
    client_socket.close()