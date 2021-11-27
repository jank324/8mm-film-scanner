import argparse
import glob
import os

from pidng.core import RPICAM2DNG


def main():
    parser = argparse.ArgumentParser(description="Convert Raspberry Pi Bayer JPEGs to DNGs.")
    parser.add_argument("directory", help="Directory with the JPEG files")
    parser.add_argument("--delete", action="store_true")
    args = parser.parse_args()

    filepaths = glob.glob(f"{args.directory}/frame-*.jpg")
    
    d = RPICAM2DNG()
    for filepath in filepaths:
        print(f"Converting {filepath}")
        d.convert(filepath)

        if args.delete:
            os.remove(filepath)


if __name__ == "__main__":
    main()
