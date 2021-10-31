from argparse import ArgumentParser
import signal

from filmscanner import FilmScanner
from notification import EmailNotifier


if __name__ == "__main__":
    parser = ArgumentParser(description="Scan a roll of film.")
    parser.add_argument("output", help="Directory to save scanned frames to")
    parser.add_argument("nframes", type=int, help="Number of frames to scan")
    parser.add_argument("--start", type=int, default=0, help="Frame index to start with")

    args = parser.parse_args()

    scanner = FilmScanner()
    notifier = EmailNotifier()

    def cleanup_and_close(sig, frame):
        scanner.stop()
    signal.signal(signal.SIGINT, cleanup_and_close)

    try:
        n_frames = scanner.scan(args.output, n_frames=args.nframes, start_index=args.start)
    except FilmScanner.AdvanceTimeoutError as e:
        notifier.send(f"ERROR: {e}")
    else:
        notifier.send(f"Finished scanning {n_frames} frames!")
    finally:
        del(scanner)
