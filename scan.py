from argparse import ArgumentParser

from filmscanner import FilmScanner


if __name__ == "__main__":
    parser = ArgumentParser(description="Scan a roll of film.")
    parser.add_argument("output", help="Directory to save scanned frames to")
    parser.add_argument("nframes", type=int, help="Number of frames to scan")
    parser.add_argument("--start", type=int, default=0, help="Frame index to start with")

    args = parser.parse_args()

    scanner = FilmScanner()
    scanner.scan(args.output, n_frames=args.nframes, start_index=args.start)
