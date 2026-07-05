import os

from pipeline import glossary


def _write_csv(path, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write("source,target\n")
        for row in rows:
            f.write(row + "\n")


def _make_root(tmp_path, general_rows, game=None, game_rows=None):
    root = tmp_path / "glossary"
    _write_csv(str(root / "general" / "glossary.csv"), general_rows)
    if game is not None:
        _write_csv(str(root / "games" / game / "glossary.csv"), game_rows or [])
    return str(root)


def test_general_only(tmp_path, monkeypatch):
    root = _make_root(tmp_path, ["Rogue,محتال", "Cleric,كاهن"])
    monkeypatch.setattr(glossary, "GLOSSARY_ROOT", root)
    glossary._cache.clear()

    result = glossary.load_glossary(None)

    assert result == {"rogue": "محتال", "cleric": "كاهن"}


def test_game_overrides_general_on_same_term(tmp_path, monkeypatch):
    root = _make_root(
        tmp_path,
        ["Rogue,محتال"],
        game="demo",
        game_rows=["Rogue,لص"],
    )
    monkeypatch.setattr(glossary, "GLOSSARY_ROOT", root)
    glossary._cache.clear()

    result = glossary.load_glossary("demo")

    assert result["rogue"] == "لص"


def test_missing_game_folder_falls_back_to_general(tmp_path, monkeypatch):
    root = _make_root(tmp_path, ["Rogue,محتال"])
    monkeypatch.setattr(glossary, "GLOSSARY_ROOT", root)
    glossary._cache.clear()

    result = glossary.load_glossary("nonexistent-game")

    assert result == {"rogue": "محتال"}


def test_case_insensitive_keys(tmp_path, monkeypatch):
    root = _make_root(tmp_path, ["RoGuE,محتال"])
    monkeypatch.setattr(glossary, "GLOSSARY_ROOT", root)
    glossary._cache.clear()

    result = glossary.load_glossary(None)

    assert result == {"rogue": "محتال"}


def test_malformed_and_blank_rows_are_skipped(tmp_path, monkeypatch):
    root = _make_root(
        tmp_path,
        [
            "Rogue,محتال",
            "",
            "NoTarget,",
            ",NoSource",
            "  ,  ",
        ],
    )
    monkeypatch.setattr(glossary, "GLOSSARY_ROOT", root)
    glossary._cache.clear()

    result = glossary.load_glossary(None)

    assert result == {"rogue": "محتال"}


def test_empty_general_file(tmp_path, monkeypatch):
    root = _make_root(tmp_path, [])
    monkeypatch.setattr(glossary, "GLOSSARY_ROOT", root)
    glossary._cache.clear()

    result = glossary.load_glossary(None)

    assert result == {}


def test_hot_reload_on_mtime_change(tmp_path, monkeypatch):
    root = _make_root(tmp_path, ["Rogue,محتال"])
    monkeypatch.setattr(glossary, "GLOSSARY_ROOT", root)
    glossary._cache.clear()

    first = glossary.load_glossary(None)
    assert first == {"rogue": "محتال"}

    general_csv = os.path.join(root, "general", "glossary.csv")
    os.utime(general_csv, (os.path.getmtime(general_csv) + 5,) * 2)
    _write_csv(general_csv, ["Rogue,لص"])
    os.utime(general_csv, (os.path.getmtime(general_csv) + 5,) * 2)

    second = glossary.load_glossary(None)
    assert second == {"rogue": "لص"}
