import signal

from machine import FilmScanner


close_requested = False

def cleanup_and_close(sig, frame):
    scanner.close_requested = True

signal.signal(signal.SIGINT, cleanup_and_close)

scanner = FilmScanner()
scanner.run(capture=False)
