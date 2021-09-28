import socket
import struct
import threading
import time

import cv2
import numpy as np

from filmscanner import FilmScanner


class Server:

    def __init__(self, host="192.168.178.48", port=7778, jpeg_quality=50):
        self.jpeg_quality = jpeg_quality

        self.scanner = FilmScanner()
        self.scanner.camera.resolution = (1024, 768)

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((host, port))
        self.server_socket.listen()
    
    def run(self):
        print("Server is ready")
        
        client_socket, address = self.server_socket.accept()

        bgr = np.empty((768,1024,3), dtype=np.uint8)

        for _ in self.scanner.camera.capture_continuous(bgr, format="bgr", use_video_port=True):
            print("New frame")

            # TODO: Hack!
            self.scanner.camera.shutter_speed = int(1e6 * 1 / 2000)

            encode_parameters = [int(cv2.IMWRITE_JPEG_QUALITY), self.jpeg_quality]
            _, encoded = cv2.imencode(".jpeg", bgr, params=encode_parameters)
            
            payload = encoded.tobytes()
            header = struct.pack(">L", len(payload))
            message = header + payload

            client_socket.sendall(message)


def main():
    server = Server()
    server.run()


if __name__ == "__main__":
    main()
