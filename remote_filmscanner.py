import socket
import struct

import cv2
import numpy as np


class RemoteFilmScanner:

    def __init__(self, host="192.168.178.48", video_port=7778):
        self.video_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.video_socket.connect((host, video_port))

        self._recv_buffer = b""
    
    def __del__(self):
        self.video_socket.close()

    def receive_frame(self):
        header_size = struct.calcsize(">L")

        while len(self._recv_buffer) < header_size:
            self._recv_buffer += self.video_socket.recv(4096)

        header = self._recv_buffer[:header_size]
        payload_size, = struct.unpack(">L", header)

        self._recv_buffer = self._recv_buffer[header_size:]

        while len(self._recv_buffer) < payload_size:
            self._recv_buffer += self.video_socket.recv(4096)
        
        payload = self._recv_buffer[:payload_size]
        encoded = np.frombuffer(payload, dtype=np.uint8)
        bgr = cv2.imdecode(encoded, cv2.IMREAD_COLOR)

        self._recv_buffer = self._recv_buffer[payload_size:]

        return bgr
    
    def advance(self):
        self.video_socket.sendall("advance".encode("utf-8"))
