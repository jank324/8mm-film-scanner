import socket
import struct
import threading
import time

import cv2
import numpy as np

from filmscanner import FilmScanner


HOST = "192.168.178.48"
PORT = 7778
ENCODE_PARAMETERS = [int(cv2.IMWRITE_JPEG_QUALITY), 50]


def advance_in_intervals(scanner):
    while True:
        time.sleep(5)
        print("Advance start")
        scanner.advance()
        print("Advance stop")


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()

        print("Server ready")

        connection, address = s.accept()
        with connection:
            print(f"Accepted connection from {address}")

            scanner = FilmScanner()
            scanner.camera.resolution = (1024, 768)

            t = threading.Thread(target=advance_in_intervals, args=(scanner,))
            t.start()

            bgr = np.empty((768,1024,3), dtype=np.uint8)

            for _ in scanner.camera.capture_continuous(bgr, format="bgr", use_video_port=True):
                print("New frame")

                # TODO: Hack!
                scanner.camera.shutter_speed = int(1e6 * 1 / 2000)

                _, encoded = cv2.imencode(".jpeg", bgr, params=ENCODE_PARAMETERS)
                
                payload = encoded.tobytes()
                header = struct.pack(">L", len(payload))
                message = header + payload

                connection.sendall(message)


if __name__ == "__main__":
    main()
