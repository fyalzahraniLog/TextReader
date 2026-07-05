import asyncio
import logging
import os
import time
from urllib.parse import quote

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import Response

from pipeline import GLOSSARY_ROOT, load_glossary, ocr_image, pin, restore, synthesize, translate_text

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("textreader")

app = FastAPI()

MAX_IMAGE_BYTES = 8 * 1024 * 1024


# Stage wrappers: the implementations live in pipeline/ (shared with the demo
# app); these module-level names are the seams the tests monkeypatch.
def _ocr(image_bytes: bytes) -> str:
    return ocr_image(image_bytes)


def _translate(text: str) -> str:
    return translate_text(text)


async def _synthesize(text: str) -> bytes:
    return await synthesize(text)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/games")
async def games():
    games_root = os.path.join(GLOSSARY_ROOT, "games")
    if not os.path.isdir(games_root):
        return {"games": []}
    return {
        "games": sorted(
            name for name in os.listdir(games_root)
            if os.path.isdir(os.path.join(games_root, name))
        )
    }


@app.post("/process")
async def process(file: UploadFile = File(...), game: str = Form("")):
    image_bytes = await file.read()
    if len(image_bytes) > MAX_IMAGE_BYTES:
        raise HTTPException(
            status_code=400,
            detail=f"Image is {len(image_bytes) // 1024} KB; the limit is "
                   f"{MAX_IMAGE_BYTES // (1024 * 1024)} MB",
        )

    start = time.perf_counter()
    try:
        source_text = await asyncio.to_thread(_ocr, image_bytes)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not read the uploaded image: {exc}")
    after_ocr = time.perf_counter()

    if not source_text:
        raise HTTPException(status_code=422, detail="No text detected in the selected region")

    glossary_terms = load_glossary(game or None)
    pinned_text, mapping = pin(source_text, glossary_terms)
    translated = await asyncio.to_thread(_translate, pinned_text)
    output_text = restore(translated, mapping)
    after_translate = time.perf_counter()

    audio_bytes = await _synthesize(output_text)
    after_tts = time.perf_counter()

    logger.info(
        "game=%s chars_in=%d chars_out=%d ocr_ms=%.0f translate_ms=%.0f tts_ms=%.0f total_ms=%.0f",
        game or "-",
        len(source_text),
        len(output_text),
        (after_ocr - start) * 1000,
        (after_translate - after_ocr) * 1000,
        (after_tts - after_translate) * 1000,
        (after_tts - start) * 1000,
    )

    headers = {
        "X-Source-Text": quote(source_text),
        "X-Output-Text": quote(output_text),
    }
    return Response(content=audio_bytes, media_type="audio/mpeg", headers=headers)
