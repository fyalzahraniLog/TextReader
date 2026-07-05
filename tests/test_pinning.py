from pipeline.pinning import pin, restore


def test_longest_match_wins_over_substring():
    glossary = {"combat": "قتال", "melee combat": "قتال التحام"}

    pinned, mapping = pin("Prepare for Melee Combat now.", glossary)

    assert len(mapping) == 1
    placeholder = next(iter(mapping))
    assert mapping[placeholder] == "قتال التحام"
    assert "Combat" not in pinned
    assert "Melee" not in pinned


def test_punctuation_adjacency():
    glossary = {"rogue": "محتال"}

    pinned, mapping = pin("A wild Rogue, appears!", glossary)

    assert len(mapping) == 1
    restored = restore(pinned, mapping)
    assert "محتال" in restored


def test_multiple_occurrences_of_one_term():
    glossary = {"cleric": "كاهن"}

    pinned, mapping = pin("The Cleric heals the cleric.", glossary)

    assert len(mapping) == 2
    for placeholder in mapping:
        assert placeholder in pinned


def test_restore_tolerates_mangled_spacing_and_case():
    glossary = {"rogue": "محتال"}

    _, mapping = pin("Rogue", glossary)
    placeholder = next(iter(mapping))

    mangled = placeholder.replace("T", " t ").replace("⟦", "⟦ ").replace("⟧", " ⟧")
    restored = restore(mangled, mapping)

    assert restored.strip() == "محتال"


def test_restore_logs_but_does_not_raise_on_missing_placeholder(capsys):
    mapping = {"⟦T1⟧": "محتال"}

    restored = restore("no placeholders here", mapping)

    assert restored == "no placeholders here"
    assert "failed to restore" in capsys.readouterr().out


def test_round_trip_on_realistic_dialogue_line():
    glossary = {"cavalier": "فارس", "order": "رتبة"}

    line = "The Cavalier has sworn a new Order."
    pinned, mapping = pin(line, glossary)

    assert "Cavalier" not in pinned and "Order" not in pinned

    fake_translation = pinned.replace("The", "").strip()
    restored = restore(fake_translation, mapping)

    assert "فارس" in restored
    assert "رتبة" in restored


def test_no_glossary_is_noop():
    pinned, mapping = pin("Nothing to pin here.", {})

    assert pinned == "Nothing to pin here."
    assert mapping == {}
