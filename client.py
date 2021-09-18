import pickle
import socket
import struct
import time
from typing import Deque

import cv2
import numpy as np


HOST = "192.168.178.48"
# HOST = "127.0.0.1"
PORT = 7777

frame_times = Deque(maxlen=100)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))

    data = b""
    payload_size = struct.calcsize(">L")

    t_before = time.time()

    while True:
        while len(data) < payload_size:
            data += s.recv(4096)
                
        packed_size = data[:payload_size]
        data = data[payload_size:]
        message_size = struct.unpack(">L", packed_size)[0]
        while len(data) < message_size:
            data += s.recv(4096)
        frame_data = data[:message_size]
        data = data[message_size:]

        encoded = pickle.loads(frame_data, fix_imports=True, encoding="bytes")
        frame = cv2.imdecode(encoded, cv2.IMREAD_COLOR)

        cv2.imshow("Live View", frame)
        cv2.waitKey(1)

        t_now = time.time()
        dt = t_now - t_before
        frame_times.append(dt)
        t_before = t_now

        nfps = 1 / dt
        mfps = 1 / np.mean(frame_times)
        print(f"FPS = {nfps:4.2f} / {mfps:4.2f} ({1 / np.std(frame_times):4.2f})")
