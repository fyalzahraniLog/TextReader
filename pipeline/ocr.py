import io
import os
import sys

import pytesseract
from PIL import Image, ImageOps

# OCR tuning, adjustable without a rebuild (Docker: docker-compose.yml
# environment; demo: set the env var before launch). Not yet validated
# against real game screenshots (see plan.md Phase 3) — the defaults match
# the working Phase 0 config.
OCR_PSM = os.environ.get("OCR_PSM", "6")
OCR_PREPROCESS = os.environ.get("OCR_PREPROCESS", "").strip().lower() in ("1", "true", "yes")


def _configure_tesseract() -> None:
    """Point pytesseract at the right binary for this host.

    Priority: TESSERACT_CMD env var > Tesseract bundled with the frozen demo
    (resolved relative to the executable, never a system install) > whatever
    is on PATH (the Docker image).
    """
    cmd = os.environ.get("TESSERACT_CMD")
    if not cmd and getattr(sys, "frozen", False):
        bundle_dir = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
        bundled = os.path.join(bundle_dir, "tesseract", "tesseract.exe")
        if os.path.isfile(bundled):
            cmd = bundled
            os.environ.setdefault(
                "TESSDATA_PREFIX", os.path.join(bundle_dir, "tesseract", "tessdata")
            )
    if cmd:
        pytesseract.pytesseract.tesseract_cmd = cmd


_configure_tesseract()


def ocr_image(image_bytes: bytes) -> str:
    image = Image.open(io.BytesIO(image_bytes))
    if OCR_PREPROCESS:
        image = ImageOps.grayscale(image)
        image = image.resize((image.width * 2, image.height * 2), Image.LANCZOS)
    return pytesseract.image_to_string(image, config=f"--oem 3 --psm {OCR_PSM}").strip()
