from datetime import datetime
import queue
from threading import Event


def format_sse(data, event=None):
    message = f"data: {data}\n\n"
    if event is not None:
        message = f"event: {event}\n{message}"
    return message


class SSEMessenger:

    def __init__(self):
        self.subscribers = []

    def subscribe(self):
        q = queue.Queue(maxsize=5)
        self.subscribers.append(q)

        def generator():
            while True:
                message = q.get()   # Blocks when queue is empty
                yield message

        return generator()

    def send(self, event, data):
        message = format_sse(data, event=event)
        for i in reversed(range(len(self.subscribers))):
            try:
                self.subscribers[i].put_nowait(message)
            except queue.Full:
                del self.subscribers[i]
    

class Callback:

    def __init__(self):
        self.scanner = None

    def setup(self, scanner):
        self.scanner = scanner
    
    def on_advance_start(self):
        pass

    def on_advance_end(self):
        pass

    def on_fast_forward_start(self):
        pass

    def on_fast_forward_end(self):
        pass

    def on_light_on(self):
        pass

    def on_light_off(self):
        pass

    def on_scan_start(self):
        pass

    def on_scan_end(self):
        pass

    def on_zoom_in(self):
        pass

    def on_zoom_out(self):
        pass


class CallbackList(Callback):

    def __init__(self, callbacks):
        self.callbacks = callbacks

        self.scanner = None
    
    def setup(self, scanner):
        for callback in self.callbacks:
            callback.setup(scanner)
    
    def on_advance_start(self):
        for callback in self.callbacks:
            callback.on_advance_start()

    def on_advance_end(self):
        for callback in self.callbacks:
            callback.on_advance_end()

    def on_fast_forward_start(self):
        for callback in self.callbacks:
            callback.on_fast_forward_start()

    def on_fast_forward_end(self):
        for callback in self.callbacks:
            callback.on_fast_forward_end()

    def on_light_on(self):
        for callback in self.callbacks:
            callback.on_light_on()

    def on_light_off(self):
        for callback in self.callbacks:
            callback.on_light_off()

    def on_scan_start(self):
        for callback in self.callbacks:
            callback.on_scan_start()

    def on_scan_end(self):
        for callback in self.callbacks:
            callback.on_scan_end()
    
    def on_zoom_in(self):
        for callback in self.callbacks:
            callback.on_zoom_in()
    
    def on_zoom_out(self):
        for callback in self.callbacks:
            callback.on_zoom_out()


class LightToggleManager(Callback):

    def __init__(self):
        self.messenger = SSEMessenger()

    def on_light_on(self):
        self.messenger.send("on", True)
    
    def on_light_off(self):
        self.messenger.send("on", False)
    
    def on_scan_start(self):
        self.messenger.send("enabled", False)

    def on_scan_end(self):
        self.messenger.send("enabled", False)


class AdvanceTriggerManager(Callback):

    def __init__(self):
        self.messenger = SSEMessenger()

    def on_advance_start(self):
        if not (self.scanner.is_fast_forwarding or self.scanner.is_scanning):
            self.messenger.send("on", True)
            self.messenger.send("enabled", False)
    
    def on_advance_end(self):
        if not (self.scanner.is_fast_forwarding or self.scanner.is_scanning):
            self.messenger.send("on", False)
            self.messenger.send("enabled", True)
        
    def on_fast_forward_start(self):
        self.messenger.send("enabled", False)
    
    def on_fast_forward_end(self):
        self.messenger.send("enabled", True)
    
    def on_scan_start(self):
        self.messenger.send("enabled", False)
    
    def on_scan_end(self):
        self.messenger.send("enabled", True)


class FastForwardToggleManager(Callback):

    def __init__(self):
        self.messenger = SSEMessenger()
    
    def on_advance_start(self):
        if not (self.scanner.is_fast_forwarding or self.scanner.is_scanning):
            self.messenger.send("enabled", False)
    
    def on_advance_end(self):
        if not (self.scanner.is_fast_forwarding or self.scanner.is_scanning):
            self.messenger.send("enabled", True)
    
    def on_fast_forward_start(self):
        self.messenger.send("on", True)
    
    def on_fast_forward_end(self):
        self.messenger.send("on", False)
    
    def on_scan_start(self):
        self.messenger.send("enabled", False)
    
    def on_scan_end(self):
        self.messenger.send("enabled", True)


class ZoomToggleManager(Callback):

    def __init__(self):
        self.messenger = SSEMessenger()
    
    def on_zoom_in(self):
        self.messenger.send("on", True)
    
    def on_zoom_out(self):
        self.messenger.send("on", False)
    
    def on_scan_start(self):
        self.messenger.send("enabled", False)
    
    def on_scan_end(self):
        self.messenger.send("enabled", True)


class ScanStateManager(Callback):

    def __init__(self):
        self.messenger = SSEMessenger()
    
    def on_scan_start(self):
        self.messenger.send("isScanning", True)
    
    def on_scan_end(self):
        self.messenger.send("isScanning", False)


class Viewer:

    def __init__(self, scanner):
        self.scanner = scanner

        self.event = Event()
        self.last_access = datetime.now()
    
    def notify(self):
        self.event.set()
    
    def view(self):
        while True:
            self.event.wait()
            yield self.scanner.preview_frame
            self.event.clear()
            self.last_access = datetime.now()
