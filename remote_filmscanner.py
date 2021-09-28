import pickle
import socket
import struct

import cv2
import numpy as np


class RemoteFilmScanner:

    def __init__(self, host="192.168.178.48", video_port=7778):
        self.video_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.video_socket.connect((host, video_port))
    
    def __del__(self):
        self.video_socket.close()

    def receive_frame(self):
        message = b""
        header_size = struct.calcsize(">L")

        while len(message) < header_size:
            message += self.video_socket.recv(4096)

        header = message[:header_size]
        payload_size, = struct.unpack(">L", header)

        payload = message[header_size:]
        while len(payload) < payload_size:
            payload += self.video_socket.recv(4096)
        
        encoded = np.frombuffer(payload, dtype=np.uint8)
        bgr = cv2.imdecode(encoded, cv2.IMREAD_COLOR)

        return bgr
    
    def advance(self):
        self.video_socket.sendall("advance".encode("utf-8"))
