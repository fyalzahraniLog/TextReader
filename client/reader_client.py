import ctypes
import io
import os
import threading
import tkinter as tk
from tkinter import messagebox
from urllib.parse import unquote

import keyboard
import pygame
import requests
from PIL import ImageGrab

from audio import init_mixer
from overlay import RegionOverlay
from settings import settings
from settings_gui import SettingsWindow
from toast import Toast

SINGLE_INSTANCE_MUTEX_NAME = "Global\\TextReaderClientSingleInstance"
ERROR_ALREADY_EXISTS = 183


def acquire_single_instance_lock():
    """Windows named mutex so a second `reader_client.py` can't register the
    same global hotkeys / bind the same audio device as a running instance.
    Returns the mutex handle to keep alive, or None if one is already held."""
    kernel32 = ctypes.windll.kernel32
    mutex = kernel32.CreateMutexW(None, False, SINGLE_INSTANCE_MUTEX_NAME)
    if ctypes.GetLastError() == ERROR_ALREADY_EXISTS:
        kernel32.CloseHandle(mutex)
        return None
    return mutex


class TextReaderClient:
    def __init__(self, root):
        self.root = root
        self.busy = False
        self.settings_window = None
        self.toast = Toast(self.root)
        self.overlay = RegionOverlay(self.root, self._on_region_selected, self._on_region_cancelled)
        self.apply_settings(register_hotkeys=False)

    def apply_settings(self, register_hotkeys: bool = True):
        """Re-read settings.ini into live state. Called at startup and again
        after the settings GUI saves, so changes take effect immediately."""
        self.server_url = settings.get("server", "url", fallback="http://localhost:8000")
        self.game = os.environ.get("TEXTREADER_GAME") or settings.get("output", "game", fallback="")
        init_mixer(settings.get("audio", "device", fallback=""))
        if register_hotkeys:
            self.register_hotkeys()

    def register_hotkeys(self):
        keyboard.unhook_all_hotkeys()
        keyboard.add_hotkey(
            settings.get("capture", "select_hotkey", fallback="ctrl+shift+c"),
            lambda: self.root.after(0, self.start_selection),
        )
        keyboard.add_hotkey(
            settings.get("capture", "settings_hotkey", fallback="ctrl+shift+s"),
            lambda: self.root.after(0, self.open_settings),
        )
        keyboard.add_hotkey(
            settings.get("capture", "quit_hotkey", fallback="ctrl+shift+q"),
            self.quit,
        )

    def start_selection(self):
        if self.busy:
            return
        self.overlay.show()

    def open_settings(self):
        if self.settings_window is not None and self.settings_window.window.winfo_exists():
            self.settings_window.window.lift()
            return
        self.settings_window = SettingsWindow(self.root, self)

    def _on_region_cancelled(self):
        pass

    def _on_region_selected(self, box):
        threading.Thread(target=self._process_region, args=(box,), daemon=True).start()

    def _process_region(self, box):
        self.busy = True
        try:
            image = ImageGrab.grab(bbox=box)
            buffer = io.BytesIO()
            image.save(buffer, format="PNG")
            buffer.seek(0)

            response = requests.post(
                f"{self.server_url}/process",
                files={"file": ("capture.png", buffer, "image/png")},
                data={"game": self.game},
                timeout=30,
            )

            if response.status_code != 200:
                message = f"Backend error {response.status_code}: {response.text}"
                print(f"[TextReader] {message}")
                self.toast.show(message, color="#ff6666")
                return

            source_text = unquote(response.headers.get("X-Source-Text", ""))
            output_text = unquote(response.headers.get("X-Output-Text", ""))
            print(f"[TextReader] source: {source_text}")
            print(f"[TextReader] output: {output_text}")
            self.toast.show(f"{source_text}\n→ {output_text}")

            self._play_audio(response.content)
        except requests.exceptions.ConnectionError:
            message = f"Backend unreachable at {self.server_url}"
            print(f"[TextReader] {message}")
            self.toast.show(message, color="#ff6666")
        except Exception as exc:
            message = f"Error: {exc}"
            print(f"[TextReader] {message}")
            self.toast.show(message, color="#ff6666")
        finally:
            self.busy = False

    def _play_audio(self, mp3_bytes: bytes):
        pygame.mixer.music.load(io.BytesIO(mp3_bytes))
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

    def quit(self):
        keyboard.unhook_all_hotkeys()
        self.root.after(0, self.root.destroy)


def main():
    mutex = acquire_single_instance_lock()
    if mutex is None:
        print("[TextReader] already running, exiting")
        root = tk.Tk()
        root.withdraw()
        messagebox.showwarning("TextReader", "TextReader is already running.")
        root.destroy()
        return

    root = tk.Tk()
    root.withdraw()

    app = TextReaderClient(root)
    app.register_hotkeys()

    root.mainloop()


if __name__ == "__main__":
    main()
