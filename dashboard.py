import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

class Dashboard:
    def __init__(self, master, app):
        self.master = master
        self.app = app
        self.master.title("TextReader Dashboard")
        self.master.geometry("800x650")
        self.master.minsize(800, 650)

        # No need to set theme here; it's set in main.py

        self.main_frame = ttk.Frame(master, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.create_header()
        self.content = ttk.Frame(self.main_frame)
        self.content.pack(fill=tk.BOTH, expand=True, pady=(20, 0))
        self.content.columnconfigure(0, weight=1)
        self.content.columnconfigure(1, weight=1)
        self.create_voice_settings_card()
        self.create_language_card()
        self.create_hotkeys_card()
        self.create_about_card()

    def create_header(self):
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill="x", pady=(0, 20))
        title = ttk.Label(
            header_frame,
            text="TextReader Dashboard",
            font=("Helvetica", 24, "bold"),
            bootstyle="inverse-primary"
        )
        title.pack(side="left")
        version = ttk.Label(
            header_frame,
            text="v1.0.0",
            font=("Helvetica", 12),
            bootstyle="inverse-secondary"
        )
        version.pack(side="left", padx=(10, 0), pady=(8, 0))

    def create_card(self, title, row, column):
        card = ttk.LabelFrame(
            self.content,
            text=title,
            padding=15,
            bootstyle="primary"  # Only use "primary", not "inverse-primary"
        )
        card.grid(row=row, column=column, padx=10, pady=10, sticky="nsew")
        return card

    def create_voice_settings_card(self):
        card = self.create_card("Voice Settings", 0, 0)
        ttk.Label(
            card,
            text="Speech Rate:",
            font=("Helvetica", 10, "bold"),
            bootstyle="inverse"
        ).pack(anchor="w", pady=(0, 5))
        
        speed_frame = ttk.Frame(card)
        speed_frame.pack(fill="x", pady=(0, 15))
        self.speed_scale = ttk.Scale(
            speed_frame,
            from_=0.5,
            to=2.0,
            value=1.0,
            command=self._update_speed,
            bootstyle="primary"
        )
        self.speed_scale.pack(side="left", fill="x", expand=True)
        self.speed_label = ttk.Label(
            speed_frame,
            text="1.00x (+0%)",
            bootstyle="inverse"
        )
        self.speed_label.pack(side="left", padx=(10, 0))

        ttk.Label(
            card,
            text="Volume:",
            font=("Helvetica", 10, "bold"),
            bootstyle="inverse"
        ).pack(anchor="w", pady=(0, 5))
        
        volume_frame = ttk.Frame(card)
        volume_frame.pack(fill="x", pady=(0, 15))
        self.volume_scale = ttk.Scale(
            volume_frame,
            from_=0,
            to=100,
            value=50,
            command=self._update_volume,
            bootstyle="primary"
        )
        self.volume_scale.pack(side="left", fill="x", expand=True)
        self.volume_label = ttk.Label(
            volume_frame,
            text="0%",
            bootstyle="inverse"
        )
        self.volume_label.pack(side="left", padx=(10, 0))

        ttk.Button(
            card,
            text="Test Voice",
            command=lambda: self.app.tts.convert("This is a test of the text to speech system"),
            bootstyle="outline-primary"
        ).pack(anchor="center", pady=(10, 0))

    def create_language_card(self):
        card = self.create_card("Language Settings", 0, 1)
        ttk.Label(
            card,
            text="Select Language:",
            font=("Helvetica", 10, "bold"),
            bootstyle="inverse"
        ).pack(anchor="w", pady=(0, 10))
        
        self.lang_var = tk.StringVar(value=self.app.current_lang)
        languages = [
            ("English", "en"),
            ("Arabic", "ar")
        ]
        
        for lang_name, lang_code in languages:
            btn = ttk.Radiobutton(
                card,
                text=lang_name,
                variable=self.lang_var,
                value=lang_code,
                command=self.app.toggle_language,
                bootstyle="toolbutton"
            )
            btn.pack(fill="x", pady=5)

    def create_hotkeys_card(self):
        card = self.create_card("Hotkey Configuration", 1, 0)
        ttk.Label(
            card,
            text="Configure Shortcuts:",
            font=("Helvetica", 10, "bold"),
            bootstyle="inverse"
        ).pack(anchor="w", pady=(0, 10))

        self.hotkey_entries = {}
        self.hotkey_defs = [
            ("Select Text Area", "ctrl+shift+c", "show_selector"),
            ("Read Selected Text", "ctrl+shift+v", "read_selection"),
            ("Toggle Language", "ctrl+shift+l", "toggle_language"),
            ("Show Dashboard", "ctrl+shift+d", "show_dashboard")
        ]

        for label, default, method in self.hotkey_defs:
            frame = ttk.Frame(card)
            frame.pack(fill="x", pady=5)
            ttk.Label(
                frame,
                text=label,
                bootstyle="inverse"
            ).pack(side="left")
            entry = ttk.Entry(frame, width=15)
            entry.insert(0, default)
            entry.pack(side="left", padx=5)
            self.hotkey_entries[method] = entry

        save_all_btn = ttk.Button(
            card,
            text="Save All",
            bootstyle="outline-success",
            command=self._save_all_hotkeys
        )
        save_all_btn.pack(pady=10)

    def create_about_card(self):
        card = self.create_card("About", 1, 1)
        ttk.Label(
            card,
            text="TextReader",
            font=("Helvetica", 14, "bold"),
            bootstyle="inverse"
        ).pack(pady=(0, 5))
        
        ttk.Label(
            card,
            text="Screen Reader with OCR & TTS",
            bootstyle="inverse-secondary"
        ).pack()
        
        ttk.Separator(card, bootstyle="primary").pack(fill="x", pady=10)
        
        info_text = """
        Developed with Python using:
        • Tesseract OCR for text recognition
        • Edge TTS for speech synthesis
        • Tkinter for the user interface
        """
        ttk.Label(
            card,
            text=info_text.strip(),
            bootstyle="inverse"
        ).pack(pady=10)

    def _update_speed(self, value):
        value = float(value)
        rate = self.app.tts._speed_to_rate(value)
        self.speed_label.config(text=f"{value:.2f}x ({rate})")
        self.app.tts.speed = value

    def _update_volume(self, value):
        value = int(float(value))
        edge_volume = int((value - 50) * 2)
        edge_volume = max(-100, min(100, edge_volume))
        self.volume_label.config(text=f"{edge_volume}%")
        self.app.tts.volume = value

    def _save_all_hotkeys(self):
        import keyboard
        from tkinter import messagebox
        errors = []
        for label, _, method in self.hotkey_defs:
            entry = self.hotkey_entries[method]
            new_hotkey = entry.get().strip()
            try:
                func = getattr(self.app, method)
                keyboard.add_hotkey(new_hotkey, func)
            except Exception as e:
                errors.append(f"{label}: {new_hotkey} ({e})")
        if errors:
            messagebox.showerror("Hotkey Error", "Some hotkeys could not be set:\n" + "\n".join(errors))
        else:
            messagebox.showinfo("Success", "All hotkeys saved successfully!")

    def show(self):
        self.master.mainloop()
