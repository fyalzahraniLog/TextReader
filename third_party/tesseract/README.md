# Portable Tesseract for the demo build

The Phase 5 demo (`demo.spec`) bundles Tesseract INSIDE `TextReaderDemo.exe`
and resolves it relative to the executable (`pipeline/ocr.py`). It never uses
a system install — end users need nothing pre-installed.

This folder holds the portable copy the build packs in. Binaries are NOT
committed (see `.gitignore`); populate it once per build machine:

1. Install Tesseract from the UB-Mannheim build
   (https://github.com/UB-Mannheim/tesseract/wiki) on any Windows machine —
   English language data is included by default. Any temp location is fine.
2. Copy the contents of the install folder here, so you end up with:

   ```
   third_party/tesseract/
     tesseract.exe
     *.dll                      (all DLLs from the install folder)
     tessdata/eng.traineddata
   ```

3. (Optional) Uninstall Tesseract again — the copy here is all the build
   needs. You can delete everything under `tessdata/` except
   `eng.traineddata` to shrink the exe.

`tools/build_demo.ps1` verifies this layout before invoking PyInstaller.

Note: the dev/runtime Tesseract still lives in the Docker image (CLAUDE.md
rule). This folder exists only to feed the demo build — nothing in the repo
references a Windows system install path.
