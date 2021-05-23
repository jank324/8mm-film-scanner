import cv2
import numpy as np

from filmscanner import FilmScanner


if __name__ == "__main__":

    scanner = FilmScanner()

    scanner.camera.resolution = (1024, 768)
    scanner.camera.framerate = 24

    focus_peaking = False
    grid = False

    bgr = np.empty((768,1024,3), dtype=np.uint8)

    for _ in scanner.camera.capture_continuous(bgr, format="bgr", use_video_port=True):
        if focus_peaking:
            grey = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(grey, 0, 255)
            overlay = cv2.add(bgr, cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR))
            
            cv2.imshow("Live View", overlay)
        elif grid:
            color = (255, 255, 255)
            for y in np.linspace(0, bgr.shape[0], 10)[1:]:
                cv2.line(bgr, (0,int(y)), (bgr.shape[1],int(y)), color)
            for x in np.linspace(0, bgr.shape[1], 10)[1:]:
                cv2.line(bgr, (int(x),0), (int(x),bgr.shape[0]), color)
            
            cv2.imshow("Live View", bgr)
        else:
            cv2.imshow("Live View", bgr)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        elif key == ord("a"):
            scanner.advance()
        elif key == ord("f"):
            focus_peaking = True
            grid = False
        elif key == ord("g"):
            grid = True
            focus_peaking = False
        elif key == ord("n"):
            focus_peaking = False
            grid = False
    
    cv2.destroyAllWindows()
