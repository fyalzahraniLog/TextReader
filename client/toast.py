import tkinter as tk


class Toast:
    """Small transient on-screen notification.

    Console output isn't visible while a game has focus during a live
    stream, so captures/errors need an on-screen line too. Safe to call
    `show()` from any thread — it marshals the actual widget creation onto
    the Tk main loop via `after(0, ...)`.
    """

    def __init__(self, root):
        self.root = root

    def show(self, message: str, duration_ms: int = 3000, color: str = "white") -> None:
        display = message if len(message) <= 200 else message[:197] + "..."

        def _show():
            popup = tk.Toplevel(self.root)
            popup.overrideredirect(True)
            popup.attributes("-topmost", True)
            popup.configure(bg="black")
            popup.geometry("+30+30")
            label = tk.Label(
                popup, text=display, font=("Consolas", 10), bg="black", fg=color,
                justify="left", wraplength=500,
            )
            label.pack(padx=10, pady=6)
            popup.after(duration_ms, popup.destroy)

        self.root.after(0, _show)
