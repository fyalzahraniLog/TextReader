# TextReader — Implementation Plan

Executable plan for Claude Code. Work top to bottom; check off `[x]` as you go.
Current state: Phases 0–3 are implemented and covered by the test suite
(`tests/`, 21 passing). Phase 5 (public demo release) is the active phase.

## Phase 0 — existing skeleton (done, do not rebuild)

- [x] `server/app.py` — FastAPI, `POST /process`: PNG → Tesseract OCR (eng,
      `--oem 3 --psm 6`) → GoogleTranslator → edge-tts (`ar-SA-HamedNeural`)
      → MP3 response. Blocking work via `asyncio.to_thread`.
- [x] `server/Dockerfile` (python:3.12-slim + tesseract-ocr-eng),
      `docker-compose.yml` publishing port 8000.
- [x] `client/reader_client.py` — Tk overlay region select, `keyboard`
      hotkeys, `pygame` playback, worker-thread pipeline call.

## Phase 1 — glossary layer (correctness core; highest priority)

Folder scaffold:

- [x] Create `glossary/general/glossary.csv` (UTF-8, header `source,target`)
      seeded with common CRPG terms, e.g.:
      `Cavalier,فارس` · `Order,رتبة` · `Rogue,محتال` · `Cleric,كاهن` ·
      `Feat,موهبة` · `Melee Combat,قتال التحام` · `Ranged Combat,قتال بعيد المدى`
- [x] Create `glossary/general/references.md` — curation notes/sources for
      humans and the offline agent. NOT loaded at runtime.
- [x] Create `glossary/games/pathfinder-wotr/glossary.csv` with game-specific
      proper nouns, e.g. `Terendelev,تيرنديليف` · `Hulrun,هولرون` ·
      `Daeran,ديران` · `Kenabres,كينابرس`
- [x] Mount `./glossary` read-only into the container in `docker-compose.yml`
      (`volumes: - ./glossary:/app/glossary:ro`) so CSV edits need no rebuild.

Loader (`server/glossary.py`):

- [x] `load_glossary(game: str | None) -> dict[str, str]` — read general CSV,
      then game CSV if present; game entries override general on the same
      source term. Case-insensitive source matching; strip whitespace; skip
      blank/malformed rows. Cache per (game, file-mtime) so edits hot-reload.
- [x] Unit tests in `tests/test_glossary.py`: override precedence, missing
      game folder, case-insensitivity, malformed rows, empty files.

Pre-translation pinning (`server/pinning.py`):

- [x] `pin(text, glossary) -> (pinned_text, mapping)` — replace each matched
      source term with a placeholder token the translator will pass through
      (format: `⟦T1⟧`, `⟦T2⟧` …). Match longest terms first (so
      "Melee Combat" wins over "Combat"); word-boundary regex, case-insensitive.
- [x] `restore(translated_text, mapping) -> str` — replace each placeholder
      with the Arabic target. Placeholders that come back altered by MT
      (spacing/case) must still be found — use a tolerant regex
      (`⟦\s*T\s*1\s*⟧`-style). Log any placeholder that fails to restore.
- [x] Wire into `/process`: accept new form field `game: str = Form("")`;
      pipeline becomes OCR → pin → translate → restore → TTS. Empty/unknown
      game ⇒ general glossary only.
- [x] Unit tests in `tests/test_pinning.py`: longest-match-first, punctuation
      adjacency, multiple occurrences of one term, placeholder survival with
      mangled spacing, round-trip on a realistic dialogue line.
- [x] Update `client/reader_client.py` to send `game` (from settings, Phase 2).

## Offline tooling — term extraction (agent loop; OFFLINE only)

`tools/extract_terms.py` mines game text for glossary candidates — never
called from the runtime path.

- [x] Extractor: walks any JSON recursively (schema-agnostic — works on WotR's
      `Wrath_Data/StreamingAssets/Localization/enGB.json`) or TXT dumps;
      strips `{...}`/`<...>`/`[...]` markup; finds capitalized terms/phrases
      incl. "of the" connectors; normalizes leading/trailing articles
      ("The Cavalier" → "Cavalier"); frequency-ranks; keeps one sample
      context per term; excludes terms already in general or game glossaries.
      Output: `glossary/games/<game>/candidates.csv` (term,count,context).
      Usage: `python tools/extract_terms.py enGB.json --game pathfinder-wotr`
- [ ] Curation flow (agent or human): review `candidates.csv`, decide Arabic
      targets, append accepted rows to the game's `glossary.csv`. An agent may
      propose targets, but a human approves before merge; note decisions in
      `glossary/general/references.md`.
- [ ] Optional improvements when needed: `--top N` cap; frequency-in-context
      weighting (terms that appear in tooltips/rules strings rank higher if
      the JSON exposes key names hinting at string type); dedupe
      singular/plural ("Cavalier"/"Cavaliers").

## Phase 2 — client config GUI (Tkinter, tabbed)

- [x] `client/settings.ini` + tiny settings module (`client/settings.py`,
      configparser): `[server] url` · `[capture] select_hotkey,
      settings_hotkey, quit_hotkey` · `[output] lang, game` · `[audio] device`.
      Missing sections/keys are auto-repaired on load instead of crashing.
- [x] Tabbed window (`client/settings_gui.py`, open with Ctrl+Shift+S):
      **General** (backend URL, target language, active-game dropdown listing
      `glossary/games/*` via `GET /games`), **Hotkeys** (rebind select/settings/
      quit), **Audio** (output-device dropdown + test-sound button), **About**.
- [x] Audio routing (`client/audio.py`): enumerate output devices via
      `pygame._sdl2.audio.get_audio_device_names` and play through the
      selected one via `pygame.mixer.init(devicename=...)`, so users can
      target a virtual cable (VB-Audio) and OBS captures the voice on its own
      channel; re-inits the mixer on device change. `sounddevice` remains the
      documented fallback if this enumeration proves unreliable elsewhere.
- [x] `GET /games` on the backend: list subfolder names of `glossary/games/`.
- [x] Persist settings on Save; apply hotkey rebinding live
      (`keyboard.unhook_all_hotkeys` → `add_hotkey` via `register_hotkeys()`).

## Phase 3 — hardening

- [x] Backend: request logging (game, chars in/out, per-stage ms) via stdlib
      `logging`; clear 4xx messages (image size in KB vs limit, decode
      failure, no-text-detected); cap image size (reject > 8 MB).
- [x] Client: on-screen toast (`client/toast.py`, thread-safe via
      `after(0, ...)`) plus console line showing OCR + translated text per
      capture; graceful "backend unreachable" toast on `ConnectionError`;
      single-instance guard via a Windows named mutex
      (`acquire_single_instance_lock` in `reader_client.py`).
- [x] OCR tuning mechanism: `OCR_PSM` and `OCR_PREPROCESS` (grayscale + 2×
      upscale) env vars in `server/app.py`, documented in
      `docker-compose.yml`. **Not yet validated against real game
      screenshots** — revisit once real captures are on hand.
- [x] `tests/test_api.py`: happy path (200, audio + headers), glossary
      pinning through `/process`, no-text-detected (422), bad image (400),
      oversized image (400), `/health`, `/games`. Stage functions mocked via
      `monkeypatch` to keep the suite hermetic; `tests/requirements.txt`
      documents what's needed to run it outside Docker.

## Phase 4 — documented swap-ins (do not build until asked)

- [ ] **VLM translation** (`server/engines/vlm.py`): screenshot → Arabic in
      one step via Ollama (Qwen-VL), OpenAI-compatible endpoint on :11434;
      add an `ollama` service to compose. Glossary goes into the prompt
      instead of pinning. Same `/process` contract — client unchanged.
- [x] **Cloned-voice TTS** (`server/engines/tts_xtts.py`): behind the same
      synth interface as edge-tts (`server/engines/tts_edge.py`); selected
      via `TTS_ENGINE=xtts` env var, activates when a reference clip exists
      at `voice/reference.wav` (mounted read-only), falls back to edge-tts
      otherwise. XTTS-v2 is local/free, supports Arabic, non-commercial
      license (fine for this project). ElevenLabs remains a documented paid
      alternative — if added, surface usage in the GUI like Cohh's tool.
      Clone quality scales with reference audio; Arabic reference needed.

## Phase 5 — public demo release (goal: introduce live translation to the public)

Purpose: a demo test that pitches **on-demand live translation** as an
alternative to translating a game's full script. Success = a stranger
downloads one file, presses one hotkey over any English game, and hears
Arabic. Demo-scoped: minimum friction beats polish.

- [x] Restructure: pipeline (OCR → glossary pin → translate → TTS) moved into
      the shared `pipeline/` package (glossary, pinning, ocr, translate, tts,
      engines/), imported by BOTH the server (`server/app.py`, thin FastAPI
      host; Docker build context is now the repo root) and the new
      `client/demo_app.py` that runs it in-process. Same code, two hosts.
      `RegionOverlay` extracted to `client/overlay.py` (shared by both
      frontends). Verified: 21 tests pass, container builds and serves
      `/health` + `/games`.
- [x] Update CLAUDE.md: architecture section now leads with the host-agnostic
      pipeline module; thin client and demo app are two frontends to it.
- [x] Tesseract resolution relative to the executable (`pipeline/ocr.py`):
      `TESSERACT_CMD` env > bundled `tesseract/tesseract.exe` next to the
      frozen exe (with `TESSDATA_PREFIX` set to its tessdata) > PATH (Docker).
      Never a system install. Portable binaries are staged (not committed) in
      `third_party/tesseract/` — see its README for the one-time setup.
- [ ] PyInstaller one-file build: `demo.spec` + `tools/build_demo.ps1`
      written (bundles pipeline, glossary general + pathfinder-wotr,
      Tesseract; console kept visible for the Arabic how-to). REMAINING:
      stage portable Tesseract per `third_party/tesseract/README.md`, run
      the build script on native Windows, and smoke-test the resulting
      `dist/TextReaderDemo.exe` over a real game before zipping it with
      `README.demo.ar.md`.
- [x] First-run experience: fixed defaults (Arabic, Ctrl+Shift+C select,
      Ctrl+Shift+Q quit, game via `TEXTREADER_GAME`, default
      pathfinder-wotr), Arabic how-to printed on launch (stdout forced to
      UTF-8), ready-toast, per-capture console + toast lines with
      recognized/spoken text, Arabic error toasts (no text / no internet).
- [x] Expectation-setting in `README.demo.ar.md`: short dialogue segments
      work best; long blocks and rapid-fire use out of scope — stated up
      front.
- [x] Feedback channel: GitHub issues link in the README plus the three
      questions (which game, what broke, would you use it). A hosted form
      can be added later if issues prove too high-friction for testers.
- [x] Known frictions documented in `README.demo.ar.md`: SmartScreen
      "More info → Run anyway" (code-signing deferred), run-as-administrator
      for hotkeys, internet required.
- [x] Out of scope for the demo (explicitly): config GUI (Phase 2), audio
      device routing, VLM/voice-clone engines, installer/auto-update —
      `demo_app.py` deliberately imports none of them.

## Notes / constraints (context for any task above)

- Live-stream tool: the capture path must stay fast and deterministic. Agent
  work (glossary curation from game text, term extraction) is OFFLINE only.
- Arabic is voice-only today, so no RTL layout code exists. Any future
  on-screen Arabic (subtitles) requires proper RTL/BiDi handling — never
  naive string reversal; see the project's localization report for why
  (reversed-before-wrap inverts line order).
- edge-tts and GoogleTranslator are network services: the container needs
  internet; there are no API keys today. Keep it that way in Phases 1–3.
- Windows host: Docker Desktop/WSL2 publishes :8000 to localhost; `keyboard`
  may require an elevated terminal.
