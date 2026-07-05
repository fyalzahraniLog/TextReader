# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for the Phase 5 demo: one file, TextReaderDemo.exe.
# Build with tools/build_demo.ps1 (or: pyinstaller demo.spec --noconfirm).
#
# Bundles the shared pipeline, the glossary folder (general + the
# pathfinder-wotr showcase game), and a portable Tesseract (eng) that
# pipeline/ocr.py resolves relative to the executable — never a system
# install. Put the portable Tesseract in third_party/tesseract/ first
# (see third_party/tesseract/README.md).

import os

TESSERACT_DIR = os.path.join(SPECPATH, "third_party", "tesseract")
if not os.path.isfile(os.path.join(TESSERACT_DIR, "tesseract.exe")):
    raise SystemExit(
        "third_party/tesseract/tesseract.exe not found — the demo must bundle "
        "its own Tesseract. See third_party/tesseract/README.md."
    )
if not os.path.isfile(os.path.join(TESSERACT_DIR, "tessdata", "eng.traineddata")):
    raise SystemExit(
        "third_party/tesseract/tessdata/eng.traineddata not found — the eng "
        "language data must ship with the demo."
    )

datas = [
    (os.path.join(SPECPATH, "glossary", "general"), "glossary/general"),
    (os.path.join(SPECPATH, "glossary", "games", "pathfinder-wotr"),
     "glossary/games/pathfinder-wotr"),
    (TESSERACT_DIR, "tesseract"),
]

a = Analysis(
    [os.path.join(SPECPATH, "client", "demo_app.py")],
    pathex=[SPECPATH, os.path.join(SPECPATH, "client")],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="TextReaderDemo",
    debug=False,
    strip=False,
    upx=False,
    # Console stays visible on purpose: the Arabic how-to prints there and
    # per-capture source/output lines double as the demo's debug log.
    console=True,
)
