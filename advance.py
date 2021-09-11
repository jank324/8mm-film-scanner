from argparse import ArgumentParser
import signal

from filmscanner import FilmScanner


if __name__ == "__main__":
    parser = ArgumentParser(description="Advance (or reverse depending on mechanical setting) the film.")
    parser.add_argument("--nframes", type=int, default=0, help="Number of frames to advance")

    args = parser.parse_args()

    scanner = FilmScanner()

    def cleanup_and_close(sig, frame):
        scanner.stop()
    signal.signal(signal.SIGINT, cleanup_and_close)

    if args.nframes == 0:
        while not scanner._stop_requested:
            scanner.advance()
    else:
        scanner.advance(args.nframes)
