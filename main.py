import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
os.environ["SDL_VIDEODRIVER"] = "dummy"

import ttkbootstrap as ttk
import keyboard
import threading
import time
import datetime
from gui import CaptureUI
from ocr import extract_text
from tts import tts
from deep_translator import GoogleTranslator
from dashboard import Dashboard
from settings import settings


class TextReader:
    def __init__(self, root):
        self.root = root
        self.tts = tts
        self.ui = CaptureUI(root)
        self.current_lang = 'en'
        self.last_text = ""
        self.is_selecting = False
        self.dashboard = None
        self.start_time = time.time()

    def show_selector(self):
        if not self.is_selecting and self.root.winfo_exists():
            self.is_selecting = True
            self.root.after(0, self.ui.show)

    def register_hotkeys(self):
            # Unregister all previous hotkeys
            keyboard.unhook_all_hotkeys()
            # Register new hotkeys from settings
            hotkeys = {
                'select_area': settings.get('Hotkeys', 'select_area', fallback='ctrl+shift+c'),
                'read_text': settings.get('Hotkeys', 'read_text', fallback='ctrl+shift+v'),
                'toggle_lang': settings.get('Hotkeys', 'toggle_lang', fallback='ctrl+shift+l'),
                'show_dashboard': settings.get('Hotkeys', 'show_dashboard', fallback='ctrl+shift+d')
            }
            keyboard.add_hotkey(hotkeys['select_area'], lambda: self.root.after(0, self.show_selector))
            keyboard.add_hotkey(hotkeys['read_text'], lambda: self.root.after(0, lambda: self.read_selection(force_reread=True)))
            keyboard.add_hotkey(hotkeys['toggle_lang'], lambda: self.root.after(0, self.toggle_language))
            keyboard.add_hotkey(hotkeys['show_dashboard'], lambda: self.root.after(0, self.show_dashboard))

    def read_selection(self, force_reread=False):
        if not force_reread and not self.is_selecting:
            return
        coords = self.ui.get_coords()
        if coords:
            try:
                now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                text = extract_text(coords).strip()
                print(f"\n[{now}] Extracted text:\n{text}\n")
                if not text:
                    return
                self.last_text = text
                read_text = text
                if self.current_lang == 'ar':
                    read_text = GoogleTranslator(source='auto', target='ar').translate(text[:4900])
                print(f"[{now}] Read text:\n{read_text}\n")
                self.tts.convert(read_text, self.current_lang)
            except Exception as e:
                print(f"[Error] {e}")
        self.is_selecting = False

    def toggle_language(self):
        self.current_lang = 'ar' if self.current_lang == 'en' else 'en'
        self.show_feedback(f"Language: {self.current_lang.upper()}")
        if self.last_text:
            self.read_selection(force_reread=True)

    def show_dashboard(self):
        if not self.dashboard:
            dash_root = ttk.Toplevel(self.root)
            self.dashboard = Dashboard(dash_root, self)
        else:
            self.dashboard.master.lift()

    def set_language(self, lang):
        self.current_lang = lang
        self.show_feedback(f"Language: {self.current_lang.upper()}")
        # self.logger.info(f"Language set to {self.current_lang}")
        if self.last_text:
            self.read_selection(force_reread=True)


    def show_feedback(self, message):
        if self.root.winfo_exists():
            popup = ttk.Toplevel(self.root)
            popup.overrideredirect(True)
            popup.geometry("+30+30")
            label = ttk.Label(popup, text=message, font=('Arial', 12), background='black', foreground='white')
            label.pack()
            popup.after(1000, popup.destroy)

def main():
    root = ttk.Window(themename="darkly")
    app = TextReader(root)

    def register_keys():
        keyboard.add_hotkey('ctrl+shift+c', app.show_selector)
        keyboard.add_hotkey('ctrl+shift+v', lambda: app.read_selection(force_reread=True))
        keyboard.add_hotkey('ctrl+shift+l', app.toggle_language)
        keyboard.add_hotkey('ctrl+shift+d', app.show_dashboard)

    root.bind("<<ReadText>>", lambda e: app.read_selection())
    threading.Thread(target=register_keys, daemon=True).start()
    app.show_dashboard()
    root.mainloop()

if __name__ == "__main__":
    main()
