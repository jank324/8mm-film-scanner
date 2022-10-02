import argparse
import glob
import os
from concurrent.futures import ThreadPoolExecutor, wait

from pidng.core import RPICAM2DNG


def bayerjpg2dng(filepath, delete=False):
    print(f"Converting {filepath}")

    d = RPICAM2DNG()
    d.convert(filepath)

    if delete:
        os.remove(filepath)


def main():
    parser = argparse.ArgumentParser(
        description="Convert Raspberry Pi Bayer JPEGs to DNGs."
    )
    parser.add_argument("directory", help="Directory with the JPEG files")
    parser.add_argument("--delete", action="store_true")
    args = parser.parse_args()

    filepaths = glob.glob(f"{args.directory}/frame-*.jpg")

    executor = ThreadPoolExecutor()

    futures = [
        executor.submit(bayerjpg2dng, path, delete=args.delete) for path in filepaths
    ]
    wait(futures)


if __name__ == "__main__":
    main()
