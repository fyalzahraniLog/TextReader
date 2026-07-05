import asyncio
import os
import subprocess
import tempfile

# Path to a reference clip to clone a voice from (a few minutes of clean
# Arabic speech; quality scales with how much reference audio you provide).
# Mounted read-only in docker-compose.yml, same convention as glossary/.
REFERENCE_WAV = os.environ.get("XTTS_REFERENCE_WAV", "/app/voice/reference.wav")
DEVICE = os.environ.get("XTTS_DEVICE", "cpu")
LANGUAGE = "ar"  # this project is Arabic-output only today

_model = None  # lazy singleton: loading the XTTS-v2 checkpoint is expensive


def is_configured() -> bool:
    """True once a reference clip has been dropped in — no restart needed."""
    return os.path.isfile(REFERENCE_WAV)


def _get_model():
    global _model
    if _model is None:
        # XTTS-v2 ships under Coqui's non-commercial CPML license; accepting
        # it is required for non-interactive (headless) model download.
        os.environ.setdefault("COQUI_TOS_AGREED", "1")
        from TTS.api import TTS  # heavy import (torch et al.); deferred until needed

        _model = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(DEVICE)
    return _model


def _synthesize_blocking(text: str) -> bytes:
    model = _get_model()
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as wav_file:
        wav_path = wav_file.name
    mp3_path = wav_path[:-4] + ".mp3"
    try:
        model.tts_to_file(
            text=text,
            speaker_wav=REFERENCE_WAV,
            language=LANGUAGE,
            file_path=wav_path,
        )
        # Convert to MP3 so the engine swap is invisible to /process's contract.
        subprocess.run(
            ["ffmpeg", "-y", "-i", wav_path, "-codec:a", "libmp3lame", mp3_path],
            check=True,
            capture_output=True,
        )
        with open(mp3_path, "rb") as f:
            return f.read()
    finally:
        for path in (wav_path, mp3_path):
            if os.path.exists(path):
                os.remove(path)


async def synthesize(text: str) -> bytes:
    return await asyncio.to_thread(_synthesize_blocking, text)
