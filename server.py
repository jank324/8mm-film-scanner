import socket
import struct
import threading

import cv2
import numpy as np

from filmscanner import FilmScanner


class Server:

    # TODO: Host will fail if it has other IP
    def __init__(self, host="192.168.178.48", port=7778, jpeg_quality=50):
        self.host = host
        self.port = port
        self.jpeg_quality = jpeg_quality

        self.close_requested = False

        self.scanner = FilmScanner()
        self.scanner.camera.resolution = (1024, 768)

        self.send_lock = threading.Lock()
    
    def run(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host,self.port))
        self.server_socket.listen()

        print("Server is ready")
        self.client_socket, address = self.server_socket.accept()

        listen_thread = threading.Thread(target=self.listen)
        stream_thread = threading.Thread(target=self.stream_live_view)
        scanner_thread = threading.Thread()

        listen_thread.start()
        stream_thread.start()
                
        listen_thread.join()
        stream_thread.join()

        self.client_socket.close()

    def listen(self):
        while True:
            message = self.client_socket.recv(4096)
            if message.decode("utf-8") == "advance":
                self.scanner.advance()
            elif not message or self.close_requested:
                break

    def send(self, message):
        with self.send_lock:
            self.client_socket.sendall(message)
    
    def stream_live_view(self):
        bgr = np.empty((768,1024,3), dtype=np.uint8)

        for _ in self.scanner.camera.capture_continuous(bgr, format="bgr", use_video_port=True):

            # TODO: Hack!
            self.scanner.camera.shutter_speed = int(1e6 * 1 / 2000)

            encode_parameters = [int(cv2.IMWRITE_JPEG_QUALITY), self.jpeg_quality]
            _, encoded = cv2.imencode(".jpeg", bgr, params=encode_parameters)
            
            payload = encoded.tobytes()
            header = struct.pack(">L", len(payload))
            message = header + payload

            self.send(message)

            if self.close_requested:
                break


def main():
    server = Server()
    server.run()


if __name__ == "__main__":
    main()
