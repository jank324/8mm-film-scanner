import cv2

from remote_filmscanner import RemoteFilmScanner


scanner = RemoteFilmScanner(host="192.168.178.48", video_port=7777)

while True:
    frame = scanner.receive_frame()
    cv2.imshow("Live View", frame)
    cv2.waitKey(1)
