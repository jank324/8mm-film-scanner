import glob
import pickle
import socket
import struct
import time

import cv2
import numpy as np


HOST = "192.168.178.48"
PORT = 7777

ENCODE_PARAMETERS = [int(cv2.IMWRITE_JPEG_QUALITY), 50]

paths = glob.glob("stream_test/*.jpg")
images = [cv2.imread(path, cv2.IMREAD_COLOR) for path in paths]

i = 0

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()

    print("Server ready")

    connection, address = s.accept()
    with connection:
        print(f"Accepted connection from {address}")

        while True:
            # color = np.random.randint(0, 255, size=3)
            # image = np.zeros((768,1024,3), dtype=np.uint8)
            # image[:] = color
            image = images[i]

            encoded = cv2.imencode(".jpeg", image, params=ENCODE_PARAMETERS)[1]
            data = pickle.dumps(encoded)
            size = len(data)
            message = struct.pack(">L", size) + data

            connection.sendall(message)

            i = (i + 1) % len(images)
            time.sleep(0.1)
