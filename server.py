import socket
import struct
import threading

import cv2
import numpy as np

from filmscanner import FilmScanner
import message


class Server:

    # TODO: Host will fail if it has other IP
    def __init__(self, host="192.168.178.48", port=7778, ):
        self.host = host
        self.port = port

        self.scanner = FilmScanner()
        self.scanner.camera.resolution = (1024, 768)

        self.send_lock = threading.Lock()
    
    def run(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host,self.port))
        self.server_socket.listen()

        while True:
            self.close_requested = False
            print("Server is ready")
            self.client_socket, address = self.server_socket.accept()
            print("Connection accepted")

            listen_thread = threading.Thread(target=self.listen)
            stream_thread = threading.Thread(target=self.stream_live_view)
            scanner_thread = threading.Thread()

            listen_thread.start()
            stream_thread.start()
                    
            listen_thread.join()
            stream_thread.join()

            self.client_socket.close()
            print("Connection closed")

    def listen(self):
        while not self.close_requested:
            msg = self.receive_message()

            if isinstance(msg, message.Advance):
                self.scanner.advance()
            elif not msg:
                self.close_requested = True
            
    def receive_message(self):
        if not self.client_socket.recv(4096):
            return None

        size_length = struct.calcsize(">L")

        while len(self._recv_buffer) < size_length:
            self._recv_buffer += self.client_socket.recv(4096)

        length_bytes = self._recv_buffer[:size_length]
        length, = struct.unpack(">L", length_bytes)

        while len(self._recv_buffer) < length:
            self._recv_buffer += self.client_socket.recv(4096)
        
        msg = self._recv_buffer[:length]

        self._recv_buffer = self._recv_buffer[length:]

        return message.deserialize(msg)

    def send(self, message):
        with self.send_lock:
            self.client_socket.sendall(message.serialized)
    
    def stream_live_view(self):
        bgr = np.empty((768,1024,3), dtype=np.uint8)

        for _ in self.scanner.camera.capture_continuous(bgr, format="bgr", use_video_port=True):

            # TODO: Hack!
            self.scanner.camera.shutter_speed = int(1e6 * 1 / 2000)

            msg = message.Image(bgr)
            self.send(msg)

            if self.close_requested:
                break


def main():
    server = Server()
    server.run()


if __name__ == "__main__":
    main()
