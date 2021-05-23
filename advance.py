from argparse import ArgumentParser
import signal

from filmscanner import FilmScanner





if __name__ == "__main__":
    parser = ArgumentParser(description="Advance (or reverse depending on mechanical setting) the film.")
    parser.add_argument("--nframes", type=int, default=0, help="Number of frames to advance")

    args = parser.parse_args()

    scanner = FilmScanner()

    def cleanup_and_close(sig, frame):
        scanner.close_requested = True
    signal.signal(signal.SIGINT, cleanup_and_close)

    if args.nframes == 0:
        while not scanner.close_requested:
            scanner.advance()
    else:
        for _ in range(args.nframes):
            scanner.advance()
            
            if scanner.close_requested:
                break
