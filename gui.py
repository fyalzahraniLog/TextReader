import tkinter as tk
from tkinter import Canvas

class CaptureUI:
    def __init__(self, root):
        self.root = root
        self.root.attributes('-fullscreen', True, '-alpha', 0.3)
        self.root.withdraw()
        
        self.canvas = Canvas(root, cursor="cross", bg="#111111", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.selection_start = None
        self.selection_rect = None
        self.coords = None

        self.canvas.bind("<ButtonPress-1>", self.start_selection)
        self.canvas.bind("<B1-Motion>", self.update_selection)
        self.canvas.bind("<ButtonRelease-1>", self.finalize_selection)

    def start_selection(self, event):
        self.selection_start = (event.x, event.y)
        self.selection_rect = self.canvas.create_rectangle(
            *self.selection_start, *self.selection_start,
            outline='white', width=1
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
        self.root.event_generate("<<ReadText>>")  # Keep this event
        self.root.after(100, self.root.event_generate, "<<AutoRead>>")  # New immediate trigger

    def show(self):
        self.root.deiconify()
        self.root.attributes('-topmost', True)
        self.canvas.delete("all")
        self.canvas.focus_set()

    def get_coords(self):
        return self.coords