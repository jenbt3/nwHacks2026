#feed the video feed from the raspberry pi camera to a server using sockets

import cv2
import socket
import pickle
import struct
import time

hostIP = '' # IP
port =  # port

#connect to backend server
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((hostIP, port)) #change to your server ip and port

#setup camera; 0 is default camera
cam = cv2.VideoCapture(0)
cam.set(3, 640)
cam.set(4, 480)


try:
    while True:
        #captures frame from camera; true if captured
        ret, frame = cam.read()
        
        #turn the image into bytes
        data = pickle.dumps(frame)
        
        #pack the data and send it over the network
        message = struct.pack("Q", len(data)) + data #adds photo of data
        client_socket.sendall(message)
        size = len(data) #

        #send the size of the frame, then the frame itself
        client_socket.sendall(struct.pack(">L", size) + data)
        
        if cv2.waitKey(1) == ord('q'): # exit if 'q' is pressed
            break
finally:
    cam.release()
    client_socket.close()