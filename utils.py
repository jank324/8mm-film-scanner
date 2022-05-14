from datetime import datetime
import queue
from threading import Event


def format_sse(data, event=None):
    """
    Format `data` as a server-sent Event on the topic `event`.

    Returns
    -------
    message : str
    """
    message = f"data: {data}\n\n"
    if event is not None:
        message = f"event: {event}\n{message}"
    return message


class SSEMessenger:
    """
    Messenger object that allows sending server-sent events to subscribed clients.
    """

    def __init__(self):
        self.subscribers = []

    def subscribe(self):
        """
        Subscribe to events sent by this messenger.

        Returns
        -------
         : generator
            Generator that yields server-sent events when they are sent.
        """
        q = queue.Queue(maxsize=5)
        self.subscribers.append(q)

        def generator():
            while True:
                message = q.get()   # Blocks when queue is empty
                yield message

        return generator()

    def send(self, event, data):
        """
        Send `data` to subscribers on the `event` topic.
        """
        message = format_sse(data, event=event)
        for i in reversed(range(len(self.subscribers))):
            try:
                self.subscribers[i].put_nowait(message)
            except queue.Full:
                del self.subscribers[i]
    

class BaseCallback:
    """
    Base class of callbacks for `FilmScanner` objects. Inherit from this class and overwrite one of
    its methods to react to the corresponding event. Access the `FilmScanner` class a callback is
    connected to via `self.scanner`.
    """

    def __init__(self):
        self.scanner = None

    def setup(self, scanner):
        self.scanner = scanner
    
    def on_advance_start(self):
        """
        Called before the scanner advances a frame.
        """
        pass

    def on_advance_end(self):
        """
        Called after the scanner has advances a frame.
        """
        pass

    def on_fast_forward_start(self):
        """
        Called before the scanner starts fast-forwarding.
        """
        pass

    def on_fast_forward_end(self):
        """
        Called after the scanner finished fast-forwarding.
        """
        pass

    def on_backlight_on(self):
        """
        Called after the scanner's backlight is turned on.
        """
        pass

    def on_backlight_off(self):
        """
        Called after the scanner's backlight is turned off.
        """
        pass

    def on_scan_start(self):
        """
        Called after a scan starts.
        """
        pass

    def on_scan_end(self):
        """
        Called after a scan ended.
        """
        pass

    def on_zoom_in(self):
        """
        Called after the camera zoomed in.
        """
        pass

    def on_zoom_out(self):
        """
        Called after the camera zoomed out.
        """
        pass


class CallbackList(BaseCallback):
    """
    Helper class to accumulate multiple callbacks for `FilmScanner` in one object.

    Parameters
    ----------
    callbacks : list
        List of callbacks, each of which is called when the callback events occur.
    """

    def __init__(self, callbacks):
        super().__init__()
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

    def on_backlight_on(self):
        for callback in self.callbacks:
            callback.on_backlight_on()

    def on_backlight_off(self):
        for callback in self.callbacks:
            callback.on_backlight_off()

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


class SSESendingCallback(BaseCallback):
    """
    Callback that reacts to events on the `FilmScanner` object by sending server-sent events which
    can be subscribed to.
    """

    def __init__(self):
        super().__init__()
        self.messenger = SSEMessenger()
    
    def subscribe_to_sse(self):
        """
        Subsribed to the server-sent events sent by this callback.
        """
        return self.messenger.subscribe()


class LightToggleCallback(SSESendingCallback):
    """
    Callback to handle state of the clients' light toggle.
    """

    def on_backlight_on(self):
        self.messenger.send("on", True)
    
    def on_backlight_off(self):
        self.messenger.send("on", False)
    
    def on_scan_start(self):
        self.messenger.send("enabled", False)

    def on_scan_end(self):
        self.messenger.send("enabled", False)


class AdvanceToggleCallback(SSESendingCallback):
    """
    Callback to handle state of the clients' advance toggle.
    """

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


class FastForwardToggleCallback(SSESendingCallback):
    """
    Callback to handle state of the clients' fast-forward toggle.
    """
    
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


class ZoomToggleCallback(SSESendingCallback):
    """
    Callback to handle state of the clients' zoom toggle.
    """
    
    def on_zoom_in(self):
        self.messenger.send("on", True)
    
    def on_zoom_out(self):
        self.messenger.send("on", False)
    
    def on_scan_start(self):
        self.messenger.send("enabled", False)
    
    def on_scan_end(self):
        self.messenger.send("enabled", True)


class ScanControlsCallback(SSESendingCallback):
    """
    Callback to handle state of the clients' scan control panel.
    """
    
    def on_scan_start(self):
        self.messenger.send("isScanning", True)
        self.messenger.send("path", self.scanner.output_directory)
        self.messenger.send("frames", self.scanner.n_frames)
    
    def on_scan_end(self):
        self.messenger.send("isScanning", False)


class Viewer:
    """
    Helper class to pass frames to a previewing client when they become available.
    """

    def __init__(self, scanner):
        self.scanner = scanner

        self.event = Event()
        self.last_access = datetime.now()
    
    def notify(self):
        """
        Notify this viewer that a new frame is available.
        """
        self.event.set()
    
    def view(self):
        """
        Generator that yields preview frames when this viewer is notified (that a new one is
        available).
        """
        while True:
            self.event.wait()
            yield self.scanner.preview_frame
            self.event.clear()
            self.last_access = datetime.now()
