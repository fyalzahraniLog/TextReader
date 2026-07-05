import tkinter as tk
from tkinter import Canvas


class RegionOverlay:
    """Fullscreen click-drag region picker. Runs on the Tk main loop.

    Shared by the thin client (reader_client.py) and the standalone demo
    (demo_app.py).
    """

    def __init__(self, root, on_select, on_cancel):
        self.root = root
        self.on_select = on_select
        self.on_cancel = on_cancel
        self.window = None
        self.canvas = None
        self.start = None
        self.rect = None

    def show(self):
        self.window = tk.Toplevel(self.root)
        self.window.attributes("-fullscreen", True)
        self.window.attributes("-alpha", 0.25)
        self.window.attributes("-topmost", True)
        self.window.configure(bg="black")
        self.canvas = Canvas(self.window, cursor="cross", bg="black", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<ButtonPress-1>", self._start)
        self.canvas.bind("<B1-Motion>", self._drag)
        self.canvas.bind("<ButtonRelease-1>", self._finish)
        self.window.bind("<Escape>", lambda _e: self._close(cancelled=True))
        self.canvas.focus_set()

    def _start(self, event):
        self.start = (event.x_root, event.y_root)
        self.rect = self.canvas.create_rectangle(
            event.x, event.y, event.x, event.y, outline="red", width=2
        )

    def _drag(self, event):
        if self.rect is not None:
            x0, y0 = self.canvas.coords(self.rect)[:2]
            self.canvas.coords(self.rect, x0, y0, event.x, event.y)

    def _finish(self, event):
        end = (event.x_root, event.y_root)
        box = (
            min(self.start[0], end[0]), min(self.start[1], end[1]),
            max(self.start[0], end[0]), max(self.start[1], end[1]),
        )
        self._close()
        if box[2] - box[0] > 2 and box[3] - box[1] > 2:
            self.on_select(box)
        else:
            self.on_cancel()

    def _close(self, cancelled=False):
        if self.window is not None:
            self.window.destroy()
            self.window = None
        if cancelled:
            self.on_cancel()
