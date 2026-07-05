# TextReader — screen region → Arabic voice

Select a region of the screen (live gameplay), OCR the English text, translate
to Arabic, speak it with a neural voice. Client/server split; backend in Docker.

Full implementation plan: @plan.md

## Architecture (do not violate)

- **Pipeline module** (`pipeline/`, host-agnostic): the processing stages —
  OCR → glossary pin → translate → TTS. The single source of truth; the two
  frontends below are thin hosts around it. Never fork stage logic into a
  frontend.
- **Backend container** (`server/app.py`, FastAPI, Docker): serves the
  pipeline over one endpoint: `POST /process` (PNG in → MP3 out, texts echoed
  in `X-Source-Text` / `X-Output-Text` headers, percent-encoded).
- **Host client** (`client/reader_client.py`, native Windows Python): owns
  screen capture, global hotkeys, audio playback; processing happens in the
  backend via `/process`. It never imports `pipeline`.
- **Demo app** (`client/demo_app.py`, PyInstaller one-file build via
  `demo.spec`): same capture/hotkeys/playback, but runs `pipeline` in-process
  — no Docker, no backend. Tesseract + glossary are bundled and resolved
  relative to the executable.
- The pipeline call runs on a worker thread in both frontends. Never block
  the Tk main loop.

## Hard rules

- Runtime is deterministic: glossary = CSV lookup applied as pre-translation
  pinning (protect terms → translate → restore). NO LLM calls in the live
  capture path — this tool runs during live streams.
- Glossary resolution: `glossary/general/glossary.csv` first, then
  `glossary/games/<game>/glossary.csv` on top (game overrides general).
- Tesseract lives in the Docker image (dev/server) or bundled inside the demo
  exe, resolved relative to the executable (`pipeline/ocr.py`). Never
  reference a Windows system install path like `C:\Program Files\Tesseract-OCR`.
- Arabic output is voice-only. If on-screen Arabic display is ever added,
  RTL/BiDi layout handling is required first (see plan.md §Notes).
- Keep engine choices swappable inside `pipeline/`: translation (MT now, VLM
  via Ollama later) and TTS (edge-tts now, XTTS-v2 clone behind
  `TTS_ENGINE=xtts`). Frontends must never know which engine is in use.

## Commands

- Backend: `docker compose up --build`  (health: `curl localhost:8000/health`)
- Client: `cd client && pip install -r requirements.txt && python reader_client.py`
- Demo build: `powershell -File tools\build_demo.ps1` → `dist\TextReaderDemo.exe`
  (stage portable Tesseract first — see `third_party/tesseract/README.md`;
  ship zipped with `README.demo.ar.md`)
- Client hotkeys (rebindable in the Ctrl+Shift+S settings window):
  Ctrl+Shift+C select region · Esc cancel · Ctrl+Shift+S open settings ·
  Ctrl+Shift+Q quit
- `keyboard` may need an Administrator terminal on Windows for global hotkeys.

## Conventions

- Python 3.12, type hints on public functions, no new heavy deps without need.
- Config: client settings in `client/settings.ini`; backend config via env
  vars in `docker-compose.yml`. No secrets committed.
- Tests live in `tests/`; glossary logic must have unit tests (it is the
  correctness core of the project).
