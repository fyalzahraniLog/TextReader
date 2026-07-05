import logging
import os

from .engines import tts_edge, tts_xtts

logger = logging.getLogger("textreader")

# TTS engine swap-in (see plan.md Phase 4): "edge" (default, cloud, fast) or
# "xtts" (local voice clone, needs a reference clip — see engines/tts_xtts.py).
TTS_ENGINE = os.environ.get("TTS_ENGINE", "edge").strip().lower()
_warned_xtts_not_configured = False


async def synthesize(text: str) -> bytes:
    global _warned_xtts_not_configured
    if TTS_ENGINE == "xtts":
        if tts_xtts.is_configured():
            return await tts_xtts.synthesize(text)
        if not _warned_xtts_not_configured:
            logger.warning(
                "TTS_ENGINE=xtts but no reference clip at %s; falling back to edge-tts",
                tts_xtts.REFERENCE_WAV,
            )
            _warned_xtts_not_configured = True
    return await tts_edge.synthesize(text)
