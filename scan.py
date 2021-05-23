from argparse import ArgumentParser
import os
from pathlib import Path

from picamera import PiCamera

from machine import FilmScanner


def scan(n_frames, output_directory):
    Path(output_directory).mkdir(parents=True, exist_ok=True)

    machine = FilmScanner()

    with PiCamera() as camera:
        for i in range(n_frames):
            filename = f"frame-{i:05d}.jpg"
            filepath = os.path.join(output_directory, filename)

            camera.capture(filepath, bayer=True)

            machine.advance()



if __name__ == "__main__":
    parser = ArgumentParser(description="Scan a roll of film.")
    parser.add_argument("nframes", type=int, help="Number of frames to scan")
    parser.add_argument("output", help="Directory to save scanned frames to")

    args = parser.parse_args()

    scan(args.nframes, args.output)

