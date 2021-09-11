from argparse import ArgumentParser
import signal

from filmscanner import FilmScanner
from notification import send_notification


if __name__ == "__main__":
    parser = ArgumentParser(description="Scan a roll of film.")
    parser.add_argument("output", help="Directory to save scanned frames to")
    parser.add_argument("nframes", type=int, help="Number of frames to scan")
    parser.add_argument("--start", type=int, default=0, help="Frame index to start with")

    args = parser.parse_args()

    scanner = FilmScanner()

    def cleanup_and_close(sig, frame):
        scanner.close_requested = True
    signal.signal(signal.SIGINT, cleanup_and_close)

    try:
        scanner.scan(args.output, n_frames=args.nframes, start_index=args.start)
    except FilmScanner.AdvanceTimeoutError as e:
        send_notification(f"ERROR: {e}")

    del(scanner)
