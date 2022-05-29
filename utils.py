from collections import deque
from datetime import datetime, timedelta
import json
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
        if isinstance(data, dict):
            data = json.dumps(data)
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

    def on_frame_capture(self):
        """
        Called after a frame was captured during a scan.
        """
        pass
    
    def on_last_scan_end_info_change(self):
        """
        Called when the info on how the last scan ended changed.
        """

    def on_light_on(self):
        """
        Called after the scanner's light is turned on.
        """
        pass

    def on_light_off(self):
        """
        Called after the scanner's light is turned off.
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
    
    def on_frame_capture(self):
        for callback in self.callbacks:
            callback.on_frame_capture()
    
    def on_last_scan_end_info_change(self):
        for callback in self.callbacks:
            callback.on_last_scan_end_info_change()

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


class DashboardCallback(SSESendingCallback):
    """
    Callback to send state information to the displays on the web dashboard.
    """

    def __init__(self):
        super().__init__()

        # Scan controls
        self.time_remaining = timedelta(0)
        self.str_time_remaining = "-"
        self.is_time_remaining_first_update = False

    def on_advance_start(self):
        self.messenger.send("state", self.scanner_state_dict)
    
    def on_advance_end(self):
        self.messenger.send("state", self.scanner_state_dict)
    
    def on_fast_forward_start(self):
        self.messenger.send("state", self.scanner_state_dict)
    
    def on_fast_forward_end(self):
        self.messenger.send("state", self.scanner_state_dict)

    def on_frame_capture(self):
        self.update_time_remaining()
        self.messenger.send("state", self.scanner_state_dict)

    def on_last_scan_end_info_change(self):
        self.messenger.send("state", self.scanner_state_dict)

    def on_light_on(self):
        self.messenger.send("state", self.scanner_state_dict)
    
    def on_light_off(self):
        self.messenger.send("state", self.scanner_state_dict)
    
    def on_scan_start(self):
        self.init_time_remaining_estimation()
        self.messenger.send("state", self.scanner_state_dict)
        scan_setup = {"n_frames": self.scanner.n_frames, "output_directory": self.scanner.output_directory}
        self.messenger.send("scan_setup", scan_setup)

    def on_scan_end(self):
        self.messenger.send("state", self.scanner_state_dict)
    
    def on_zoom_in(self):
        self.messenger.send("state", self.scanner_state_dict)
    
    def on_zoom_out(self):
        self.messenger.send("state", self.scanner_state_dict)
    
    @property
    def scanner_state_dict(self):
        return {
            "advance_toggle": {
                "active": self.scanner.is_advancing and not self.scanner.is_fast_forwarding,
                "enabled": self.scanner.is_advance_allowed,
            },
            "current_frame_index": self.scanner.current_frame_index,
            "fast_forward_toggle": {
                "active": self.scanner.is_fast_forwarding,
                "enabled": self.scanner.is_fast_forward_allowed or self.scanner.is_fast_forwarding,
            },
            "is_scanning": self.scanner.is_scanning,
            "is_scan_button_enabled": self.scanner.is_scanning_allowed or self.scanner.is_scanning,
            "last_scan_end_info": self.scanner.last_scan_end_info,
            "light_toggle": {
                "active": self.scanner.is_light_on,
                "enabled": self.scanner.is_light_toggle_allowed,
            },
            "time_remaining": self.str_time_remaining,
            "zoom_toggle": {
                "active": self.scanner.is_zoomed,
                "enabled": self.scanner.is_zoom_toggle_allowed,
            },
        }

    def init_time_remaining_estimation(self):
        self.t_last = datetime.now()
        self.dts = deque([], maxlen=100)
        self.time_remaining = timedelta(0)
        self.str_time_remaining = "-"

        self.is_time_remaining_first_update = True
    
    def update_time_remaining(self):
        t_now = datetime.now()
        dt = t_now - self.t_last
        self.t_last = t_now
        
        # On the first update of time remaining don't add dt to dts because it measures the duration
        # of the scan initialisation and therefore throws off the time remaining estimate.
        if self.is_time_remaining_first_update:
            self.is_time_remaining_first_update = False
            return

        self.dts.append(dt) 
        
        dt_mean = sum(self.dts, timedelta(0)) / len(self.dts)
        frames_remaining = self.scanner.n_frames - self.scanner.current_frame_index
        self.time_remaining = dt_mean * frames_remaining

        self.str_time_remaining = str(self.time_remaining).split(".")[0]


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
