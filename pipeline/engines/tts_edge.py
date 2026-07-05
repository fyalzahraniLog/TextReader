import os
import tempfile

import edge_tts

VOICE = "ar-SA-HamedNeural"


async def synthesize(text: str) -> bytes:
    communicate = edge_tts.Communicate(text, VOICE)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
        tmp_path = f.name
    try:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                with open(tmp_path, "ab") as f:
                    f.write(chunk["data"])
        with open(tmp_path, "rb") as f:
            return f.read()
    finally:
        os.remove(tmp_path)
