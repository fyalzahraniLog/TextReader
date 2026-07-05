import csv
import os
import sys


def _candidate_roots() -> list[str]:
    roots = []
    if getattr(sys, "frozen", False):
        # Frozen demo: a glossary folder next to the exe wins (users can edit
        # CSVs without a rebuild), then the copy bundled inside the one-file
        # package. Resolved relative to the executable, never a system path.
        exe_dir = os.path.dirname(sys.executable)
        roots.append(os.path.join(exe_dir, "glossary"))
        roots.append(os.path.join(getattr(sys, "_MEIPASS", exe_dir), "glossary"))
    here = os.path.dirname(os.path.abspath(__file__))
    # Parent of pipeline/: /app/glossary in the container (mounted read-only),
    # repo_root/glossary in local dev.
    roots.append(os.path.join(os.path.dirname(here), "glossary"))
    return roots


_CANDIDATE_ROOTS = _candidate_roots()
GLOSSARY_ROOT = os.environ.get("GLOSSARY_ROOT") or next(
    (p for p in _CANDIDATE_ROOTS if os.path.isdir(p)), _CANDIDATE_ROOTS[-1]
)

_cache: dict[tuple, dict[str, str]] = {}


def _general_csv_path() -> str:
    return os.path.join(GLOSSARY_ROOT, "general", "glossary.csv")


def _game_csv_path(game: str | None) -> str | None:
    if not game:
        return None
    path = os.path.join(GLOSSARY_ROOT, "games", game, "glossary.csv")
    return path if os.path.isfile(path) else None


def _mtime(path: str | None) -> float:
    if not path or not os.path.isfile(path):
        return -1.0
    return os.path.getmtime(path)


def _read_csv(path: str | None) -> dict[str, str]:
    entries: dict[str, str] = {}
    if not path or not os.path.isfile(path):
        return entries
    with open(path, "r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            if not row:
                continue
            source = (row.get("source") or "").strip()
            target = (row.get("target") or "").strip()
            if not source or not target:
                continue
            entries[source.lower()] = target
    return entries


def load_glossary(game: str | None = None) -> dict[str, str]:
    """Load the general glossary, then overlay the game glossary (if any).

    Keys are lowercased source terms. Results are cached per (game,
    file-mtime) so CSV edits hot-reload without a server restart.
    """
    general_path = _general_csv_path()
    game_path = _game_csv_path(game)
    cache_key = (game or "", _mtime(general_path), _mtime(game_path))

    cached = _cache.get(cache_key)
    if cached is not None:
        return cached

    merged = _read_csv(general_path)
    merged.update(_read_csv(game_path))

    _cache.clear()
    _cache[cache_key] = merged
    return merged
