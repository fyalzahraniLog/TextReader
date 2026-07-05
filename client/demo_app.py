"""TextReaderDemo — standalone one-file demo (plan.md Phase 5).

Runs the shared pipeline (OCR → glossary pin → translate → TTS) IN-PROCESS:
no Docker, no backend. Same pipeline code as the server — two frontends, one
pipeline. Packaged with PyInstaller via demo.spec; Tesseract and the glossary
folder ride inside the exe and are resolved relative to it.

Demo scope (deliberately minimal — see plan.md Phase 5 "out of scope"):
fixed hotkeys, default audio device, no settings GUI.
"""

import asyncio
import ctypes
import io
import os
import sys
import threading
import tkinter as tk
from tkinter import messagebox

# Running from source: make the repo-root `pipeline` package importable from
# client/. Frozen: PyInstaller bundles it, no path juggling needed.
if not getattr(sys, "frozen", False):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import keyboard
import pygame
from PIL import ImageGrab

from overlay import RegionOverlay
from pipeline import load_glossary, ocr_image, pin, restore, synthesize, translate_text
from toast import Toast

SELECT_HOTKEY = "ctrl+shift+c"
QUIT_HOTKEY = "ctrl+shift+q"
GAME = os.environ.get("TEXTREADER_GAME", "pathfinder-wotr")

SINGLE_INSTANCE_MUTEX_NAME = "Global\\TextReaderDemoSingleInstance"
ERROR_ALREADY_EXISTS = 183

HOW_TO_AR = f"""
============================================================
 TextReader — تجربة الترجمة الصوتية الفورية
============================================================
 طريقة الاستخدام:
   1. شغّل لعبتك (بالإنجليزية) واترك هذه النافذة مفتوحة.
   2. اضغط  Ctrl+Shift+C  ثم ظلّل منطقة النص بالفأرة.
   3. انتظر ثوانٍ — ستسمع الترجمة بالصوت العربي.

   Esc  لإلغاء التحديد  ·  Ctrl+Shift+Q  للخروج

 ملاحظات:
   - يعمل بشكل أفضل مع مقاطع الحوار القصيرة.
   - يحتاج اتصال إنترنت (الترجمة والصوت خدمات سحابية).
   - إذا لم تعمل الاختصارات، شغّل البرنامج كمسؤول
     (Run as administrator).
============================================================
"""


def acquire_single_instance_lock():
    """Windows named mutex so a second demo instance can't double-register
    the global hotkeys. Returns the handle to keep alive, or None."""
    kernel32 = ctypes.windll.kernel32
    mutex = kernel32.CreateMutexW(None, False, SINGLE_INSTANCE_MUTEX_NAME)
    if ctypes.GetLastError() == ERROR_ALREADY_EXISTS:
        kernel32.CloseHandle(mutex)
        return None
    return mutex


class DemoApp:
    def __init__(self, root):
        self.root = root
        self.busy = False
        self.toast = Toast(self.root)
        self.overlay = RegionOverlay(self.root, self._on_region_selected, lambda: None)
        pygame.mixer.init()
        keyboard.add_hotkey(SELECT_HOTKEY, lambda: self.root.after(0, self.start_selection))
        keyboard.add_hotkey(QUIT_HOTKEY, self.quit)

    def start_selection(self):
        if self.busy:
            return
        self.overlay.show()

    def _on_region_selected(self, box):
        threading.Thread(target=self._process_region, args=(box,), daemon=True).start()

    def _process_region(self, box):
        self.busy = True
        try:
            image = ImageGrab.grab(bbox=box)
            buffer = io.BytesIO()
            image.save(buffer, format="PNG")

            source_text = ocr_image(buffer.getvalue())
            if not source_text:
                self._report("لم يتم العثور على نص في المنطقة المحددة — جرّب تحديدًا أدق.",
                             error=True)
                return

            glossary_terms = load_glossary(GAME or None)
            pinned_text, mapping = pin(source_text, glossary_terms)
            translated = translate_text(pinned_text)
            output_text = restore(translated, mapping)

            audio_bytes = asyncio.run(synthesize(output_text))

            print(f"[TextReader] source: {source_text}")
            print(f"[TextReader] output: {output_text}")
            self.toast.show(f"{source_text}\n→ {output_text}")

            self._play_audio(audio_bytes)
        except OSError as exc:
            self._report(f"تعذّر الاتصال — تأكد من اتصال الإنترنت. ({exc})", error=True)
        except Exception as exc:
            self._report(f"خطأ: {exc}", error=True)
        finally:
            self.busy = False

    def _report(self, message: str, error: bool = False):
        print(f"[TextReader] {message}")
        self.toast.show(message, color="#ff6666" if error else "white")

    def _play_audio(self, mp3_bytes: bytes):
        pygame.mixer.music.load(io.BytesIO(mp3_bytes))
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

    def quit(self):
        keyboard.unhook_all_hotkeys()
        self.root.after(0, self.root.destroy)


def selftest() -> int:
    """No-GUI check of the packaged pipeline (`TextReaderDemo.exe --selftest`):
    bundled Tesseract + glossary offline, then the cloud stages. Exit 0 = OK."""
    from PIL import Image, ImageDraw

    image = Image.new("RGB", (620, 60), "white")
    ImageDraw.Draw(image).text((10, 20), "The Rogue meets Daeran in Kenabres.", fill="black")
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")

    source_text = ocr_image(buffer.getvalue())
    print(f"selftest OCR      : {source_text!r}", flush=True)
    glossary_terms = load_glossary(GAME or None)
    print(f"selftest glossary : {len(glossary_terms)} terms (game={GAME or '-'})", flush=True)
    if "Rogue" not in source_text:
        print("selftest FAILED: bundled Tesseract did not read the test image", flush=True)
        return 1

    try:
        pinned_text, mapping = pin(source_text, glossary_terms)
        output_text = restore(translate_text(pinned_text), mapping)
        print(f"selftest translate: {output_text}", flush=True)
        audio_bytes = asyncio.run(synthesize(output_text))
        print(f"selftest TTS      : {len(audio_bytes)} bytes", flush=True)
    except Exception as exc:
        print(f"selftest FAILED at cloud stage (internet required): {exc}", flush=True)
        return 1

    print("selftest OK", flush=True)
    return 0


def main():
    # Windows consoles often default to a legacy codepage; the how-to and the
    # per-capture lines are Arabic, so force UTF-8 (best effort).
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    if "--selftest" in sys.argv:
        if "--debug-stdio" in sys.argv:
            with open(os.path.join(os.path.dirname(sys.executable), "stdio_debug.txt"), "w") as dbg:
                dbg.write(f"stdout={sys.stdout!r}\n")
                dbg.write(f"fileno={sys.stdout.fileno() if sys.stdout else 'None'}\n")
                dbg.write(f"stderr={sys.stderr!r}\n")
            print("CP-main reached", flush=True)
            sys.stderr.write("CP-main via stderr\n")
            sys.stderr.flush()
        sys.exit(selftest())

    mutex = acquire_single_instance_lock()
    if mutex is None:
        root = tk.Tk()
        root.withdraw()
        messagebox.showwarning("TextReader", "TextReader is already running.")
        root.destroy()
        return

    print(HOW_TO_AR, flush=True)

    root = tk.Tk()
    root.withdraw()
    app = DemoApp(root)
    app.toast.show("TextReader جاهز — اضغط Ctrl+Shift+C لتحديد منطقة النص")
    root.mainloop()


if __name__ == "__main__":
    main()
