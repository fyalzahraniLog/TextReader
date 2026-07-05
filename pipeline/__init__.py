"""Host-agnostic processing pipeline: OCR → glossary pin → translate → TTS.

Imported by BOTH the FastAPI server (`server/app.py`, Docker) and the
standalone demo (`client/demo_app.py`, PyInstaller). Stage implementations
live here; each host does its own orchestration (timing, error mapping).
"""

from .glossary import GLOSSARY_ROOT, load_glossary
from .ocr import ocr_image
from .pinning import pin, restore
from .translate import translate_text
from .tts import synthesize

__all__ = [
    "GLOSSARY_ROOT",
    "load_glossary",
    "ocr_image",
    "pin",
    "restore",
    "translate_text",
    "synthesize",
]
