import threading
import tkinter as tk
from tkinter import ttk

import requests

from audio import init_mixer, list_output_devices, play_test_tone
from settings import settings


class SettingsWindow:
    """Tabbed settings window (General / Hotkeys / Audio / About)."""

    def __init__(self, root, app):
        self.root = root
        self.app = app
        self.window = tk.Toplevel(root)
        self.window.title("TextReader Settings")
        self.window.geometry("420x360")
        self.window.resizable(False, False)
        self.window.attributes("-topmost", True)

        notebook = ttk.Notebook(self.window)
        notebook.pack(fill="both", expand=True, padx=8, pady=8)

        self._build_general_tab(notebook)
        self._build_hotkeys_tab(notebook)
        self._build_audio_tab(notebook)
        self._build_about_tab(notebook)

        save_row = ttk.Frame(self.window)
        save_row.pack(fill="x", padx=8, pady=(0, 8))
        self.status_label = ttk.Label(save_row, text="")
        self.status_label.pack(side="left")
        ttk.Button(save_row, text="Save", command=self._save_all).pack(side="right")

    def _build_general_tab(self, notebook):
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="General")

        ttk.Label(tab, text="Backend URL:").grid(row=0, column=0, sticky="w", padx=8, pady=6)
        self.url_var = tk.StringVar(value=settings.get("server", "url"))
        ttk.Entry(tab, textvariable=self.url_var, width=32).grid(row=0, column=1, padx=8, pady=6)

        ttk.Label(tab, text="Target language:").grid(row=1, column=0, sticky="w", padx=8, pady=6)
        self.lang_var = tk.StringVar(value=settings.get("output", "lang", fallback="ar"))
        ttk.Combobox(
            tab, textvariable=self.lang_var, values=["ar"], state="readonly", width=29
        ).grid(row=1, column=1, padx=8, pady=6)

        ttk.Label(tab, text="Active game:").grid(row=2, column=0, sticky="w", padx=8, pady=6)
        self.game_var = tk.StringVar(value=settings.get("output", "game", fallback=""))
        self.game_combo = ttk.Combobox(
            tab, textvariable=self.game_var, values=[""], state="readonly", width=29
        )
        self.game_combo.grid(row=2, column=1, padx=8, pady=6)
        ttk.Button(tab, text="Refresh from backend", command=self._refresh_games).grid(
            row=3, column=1, sticky="e", padx=8, pady=(0, 6)
        )

        self._refresh_games()

    def _refresh_games(self):
        server_url = self.url_var.get()

        def fetch():
            games = [""]
            try:
                resp = requests.get(f"{server_url}/games", timeout=5)
                if resp.ok:
                    games += resp.json().get("games", [])
            except requests.exceptions.RequestException:
                pass
            self.window.after(0, lambda: self._apply_games(games))

        threading.Thread(target=fetch, daemon=True).start()

    def _apply_games(self, games):
        current = self.game_var.get()
        self.game_combo["values"] = games
        if current not in games:
            self.game_var.set("")

    def _build_hotkeys_tab(self, notebook):
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="Hotkeys")

        self.hotkey_vars = {}
        rows = [
            ("Select region", "select_hotkey"),
            ("Open settings", "settings_hotkey"),
            ("Quit", "quit_hotkey"),
        ]
        for i, (label, key) in enumerate(rows):
            ttk.Label(tab, text=f"{label}:").grid(row=i, column=0, sticky="w", padx=8, pady=6)
            var = tk.StringVar(value=settings.get("capture", key))
            ttk.Entry(tab, textvariable=var, width=20).grid(row=i, column=1, padx=8, pady=6)
            self.hotkey_vars[key] = var

        ttk.Label(
            tab, text="Esc cancels an in-progress region selection.", foreground="gray"
        ).grid(row=len(rows), column=0, columnspan=2, sticky="w", padx=8, pady=(12, 6))

    def _build_audio_tab(self, notebook):
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="Audio")

        ttk.Label(tab, text="Output device:").grid(row=0, column=0, sticky="w", padx=8, pady=6)
        devices = [""] + list_output_devices()
        current = settings.get("audio", "device", fallback="")
        self.device_var = tk.StringVar(value=current if current in devices else "")
        ttk.Combobox(
            tab, textvariable=self.device_var, values=devices, state="readonly", width=29
        ).grid(row=0, column=1, padx=8, pady=6)

        ttk.Button(tab, text="Test sound", command=self._test_sound).grid(
            row=1, column=1, sticky="e", padx=8, pady=6
        )

    def _test_sound(self):
        init_mixer(self.device_var.get())
        play_test_tone()

    def _build_about_tab(self, notebook):
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="About")

        ttk.Label(tab, text="TextReader", font=("Segoe UI", 14, "bold")).pack(pady=(16, 4))
        ttk.Label(tab, text="Screen region → OCR → Arabic voice").pack()
        ttk.Label(tab, text="Backend: FastAPI + Tesseract + edge-tts").pack(pady=(12, 0))

    def _save_all(self):
        settings.set("server", "url", self.url_var.get().strip())
        settings.set("output", "lang", self.lang_var.get())
        settings.set("output", "game", self.game_var.get())
        for key, var in self.hotkey_vars.items():
            settings.set("capture", key, var.get().strip())
        settings.set("audio", "device", self.device_var.get())
        settings.save()

        self.app.apply_settings()

        self.status_label.config(text="Settings saved.")
        self.window.after(2000, lambda: self.status_label.config(text=""))
