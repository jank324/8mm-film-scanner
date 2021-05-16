import signal

from machine import Machine


close_requested = False

def cleanup_and_close(sig, frame):
    machine.close_requested = True

signal.signal(signal.SIGINT, cleanup_and_close)

machine = Machine()
machine.run()
