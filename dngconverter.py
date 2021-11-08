import argparse
import glob

from pidng.core import RPICAM2DNG


def main():
    parser = argparse.ArgumentParser(description="Convert Raspberry Pi Bayer JPEGs to DNGs.")
    parser.add_argument("directory", help="Directory with the JPEG files")
    args = parser.parse_args()

    filepaths = glob.glob(f"{args.directory}/frame-*.jpg")
    
    d = RPICAM2DNG()
    for filepath in filepaths:
        print(f"Converting {filepath}")
        d.convert(filepath)


if __name__ == "__main__":
    main()
