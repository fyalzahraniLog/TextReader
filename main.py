import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
os.environ["SDL_VIDEODRIVER"] = "dummy"

from gui import CaptureUI
from ocr import extract_text
from tts import tts
import tkinter as tk
import keyboard
import threading
from deep_translator import GoogleTranslator

class TextReader:
    def __init__(self, root):
        self.root = root
        self.ui = CaptureUI(root)
        self.current_lang = 'en'
        self.last_text = ""
        self.is_selecting = False

    def show_selector(self):
        if not self.is_selecting and self.root.winfo_exists():
            self.is_selecting = True
            self.root.after(0, self.ui.show)

    def read_selection(self, force_reread=False):
        if not force_reread and not self.is_selecting:
            return
            
        if coords := self.ui.get_coords():
            try:
                text = extract_text(coords).strip()
                if not text:
                    return
                
                self.last_text = text
                
                if self.current_lang == 'ar':
                    text = GoogleTranslator(source='auto', target='ar').translate(text[:4900])
                
                tts.convert(text, 'ar' if self.current_lang == 'ar' else 'en')
            except Exception as e:
                print(f"Error: {e}")
        self.is_selecting = False

    def toggle_language(self):
        self.current_lang = 'ar' if self.current_lang == 'en' else 'en'
        self.show_feedback(f"Language: {self.current_lang.upper()}")
        if self.last_text:
            self.read_selection(force_reread=True)

    def show_feedback(self, message):
        if self.root.winfo_exists():
            popup = tk.Toplevel(self.root)
            popup.overrideredirect(True)
            popup.geometry("+30+30")
            label = tk.Label(popup, text=message, font=('Arial', 12), bg='black', fg='white')
            label.pack()
            popup.after(1000, popup.destroy)

def main():
    root = tk.Tk()
    app = TextReader(root)

    def register_keys():
        keyboard.add_hotkey('ctrl+shift+c', app.show_selector)
        keyboard.add_hotkey('ctrl+shift+v', lambda: app.read_selection(force_reread=True))
        keyboard.add_hotkey('ctrl+shift+l', app.toggle_language)

    # Auto-read when selection is made
    root.bind("<<ReadText>>", lambda e: app.read_selection())
    
    threading.Thread(target=register_keys, daemon=True).start()
    root.mainloop()

if __name__ == "__main__":
    main()