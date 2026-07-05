import io
import math
import struct
import wave

import pygame


def list_output_devices() -> list[str]:
    """Enumerate playback device names via pygame's SDL2 bindings.

    Falls back to an empty list (GUI shows "Default") if unsupported on this
    platform/pygame build; sounddevice is the documented fallback if this
    proves unreliable in practice (see docs/plan.md Phase 2).
    """
    try:
        from pygame._sdl2 import audio as sdl2_audio

        if not pygame.get_init():
            pygame.init()
        return list(sdl2_audio.get_audio_device_names(False))
    except Exception as exc:
        print(f"[TextReader] could not enumerate audio devices: {exc}")
        return []


def init_mixer(device_name: str = "") -> None:
    """(Re)initialize the mixer, optionally targeting a specific output
    device (e.g. a virtual cable for OBS to capture separately)."""
    if pygame.mixer.get_init() is not None:
        pygame.mixer.quit()
    try:
        if device_name:
            pygame.mixer.init(devicename=device_name)
        else:
            pygame.mixer.init()
    except Exception as exc:
        print(f"[TextReader] failed to init audio device '{device_name}': {exc}")
        pygame.mixer.init()


def generate_test_tone(freq: float = 440.0, duration: float = 0.4, framerate: int = 44100) -> io.BytesIO:
    """A short sine-wave beep as in-memory WAV bytes, used to test the
    selected output device without needing the backend."""
    n_samples = int(framerate * duration)
    frames = bytearray()
    for i in range(n_samples):
        sample = int(0.5 * 32767 * math.sin(2 * math.pi * freq * (i / framerate)))
        frames += struct.pack("<h", sample)

    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(framerate)
        wf.writeframes(bytes(frames))
    buffer.seek(0)
    return buffer


def play_test_tone() -> None:
    pygame.mixer.music.load(generate_test_tone())
    pygame.mixer.music.play()
