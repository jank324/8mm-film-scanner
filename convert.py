import argparse
import os

from pydng.core import RPICAM2DNG


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert .jpg files with bayer data from the Raspberry Pi camera to .dng files.")
    parser.add_argument("path", help="Path to a single image or folder of images")

    args = parser.parse_args()

    d = RPICAM2DNG()
    
    if args.path.endswith(".jpg"):
        d.convert(args.path)
    else:
        for filename in os.listdir(args.path):
            if filename.endswith(".jpg"):
                path = os.path.join(args.path, filename)
                
                d.convert(path)
