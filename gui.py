import tkinter as tk
from tkinter import Canvas

class CaptureUI:
    def __init__(
        self, root,
        overlay_color="#888888",  # Gray overlay
        overlay_alpha=0.2,       # Transparency
        selection_outline="red", # Selection border color
        selection_fill="white"   # Selection fill color
    ):
        self.root = root
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-alpha', overlay_alpha)
        self.root.withdraw()
        self.canvas = Canvas(root, cursor="cross", bg=overlay_color, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.selection_start = None
        self.selection_rect = None
        self.coords = None
        self.selection_outline = selection_outline
        self.selection_fill = selection_fill

        self.canvas.bind("<ButtonPress-1>", self.start_selection)
        self.canvas.bind("<B1-Motion>", self.update_selection)
        self.canvas.bind("<ButtonRelease-1>", self.finalize_selection)

    def start_selection(self, event):
        self.selection_start = (event.x, event.y)
        self.selection_rect = self.canvas.create_rectangle(
            *self.selection_start, *self.selection_start,
            outline=self.selection_outline, width=3, fill=self.selection_fill
        )

    def update_selection(self, event):
        if self.selection_rect:
            self.canvas.coords(
                self.selection_rect,
                *self.selection_start,
                event.x, event.y
            )

    def finalize_selection(self, event):
        x1, y1 = self.selection_start
        x2, y2 = event.x, event.y
        self.coords = (
            min(x1, x2), min(y1, y2),
            max(x1, x2), max(y1, y2)
        )
        self.root.withdraw()
        self.root.event_generate("<<ReadText>>")
        self.root.after(100, self.root.event_generate, "<<AutoRead>>")

    def show(self):
        self.root.deiconify()
        self.root.attributes('-topmost', True)
        self.canvas.delete("all")
        self.canvas.focus_set()

    def get_coords(self):
        return self.coords
