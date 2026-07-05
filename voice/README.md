# Voice reference clip (XTTS-v2 cloned voice)

This folder is mounted read-only into the backend container at
`/app/voice`. It's only used when `TTS_ENGINE=xtts` (see `plan.md` Phase 4
and `server/engines/tts_xtts.py`); the default `edge-tts` engine ignores it.

## Usage

Drop a clean, single-speaker Arabic recording at:

```
voice/reference.wav
```

(override the path with the `XTTS_REFERENCE_WAV` env var if you'd rather
name it something else). No rebuild or restart needed — the backend checks
for the file on every request and starts using it the moment it appears.
Until it exists, requests with `TTS_ENGINE=xtts` fall back to `edge-tts`
automatically (a one-time warning is logged when that happens).

## Recording notes

- **Minutes matter.** A few seconds will "work" but a few minutes of clean
  reference audio makes a real difference to how natural the clone sounds.
- Arabic reference audio specifically — the clone quality for a target
  language depends on hearing that language in the reference, not just any
  audio of the same speaker.
- Single speaker, minimal background noise/music, consistent volume.
- WAV is recommended; XTTS-v2 also accepts other formats `soundfile` can
  read, but WAV avoids any surprises.

## Enabling the engine

XTTS-v2 is a multi-GB dependency (torch + the model checkpoint), so it's not
installed by default. Build with it enabled:

```
INSTALL_XTTS=true docker compose up --build
```

then set `TTS_ENGINE=xtts` in `docker-compose.yml`'s `environment:` block.
CPU inference is slow (XTTS-v2 can take several seconds per sentence) —
this trades away some of the "fast, deterministic" live-capture latency the
default `edge-tts` path gives you; a GPU (`XTTS_DEVICE=cuda`) helps a lot.
