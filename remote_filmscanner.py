import socket
import struct

import cv2
import numpy as np

import message


class RemoteFilmScanner:

    def __init__(self, host="192.168.178.48", video_port=7778):
        self.video_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.video_socket.connect((host, video_port))

        self._recv_buffer = b""
    
    def __del__(self):
        self.video_socket.close()
    
    def _receive_message(self):
        size_length = struct.calcsize(">L")

        while len(self._recv_buffer) < size_length:
            self._recv_buffer += self.video_socket.recv(4096)

        length_bytes = self._recv_buffer[:size_length]
        length, = struct.unpack(">L", length_bytes)

        while len(self._recv_buffer) < length:
            self._recv_buffer += self.video_socket.recv(4096)
        
        msg = self._recv_buffer[:length]

        self._recv_buffer = self._recv_buffer[length:]

        return message.deserialize(msg)
    
    def receive_frame(self):
        msg = self._receive_message()
        if isinstance(msg, message.Image):
            return msg.image
        else:
            raise NotImplementedError
    
    def advance(self):
        self.video_socket.sendall(message.Advance())
