# Glossary References & Curation Guide

This folder documents *how* glossary decisions are made. Nothing here is
loaded at runtime — the runtime reads only the `glossary.csv` files.

## The pipeline (offline agent loop)

```
game text (enGB.json / dumps)
        │  tools/extract_terms.py
        ▼
games/<game>/candidates.csv        ← review queue (term, count, context)
        │  curation (agent proposes, human approves)
        ▼
games/<game>/glossary.csv          ← runtime file (source,target)
```

Run: `python tools/extract_terms.py enGB.json --game pathfinder-wotr`

---

## Curation checklist (per candidate)

Work through `candidates.csv` top-down (highest frequency = highest impact).
For each term, decide one of:

1. **ACCEPT** — it's a game term needing a fixed translation.
   Add `source,target` to the game's `glossary.csv` (or to
   `general/glossary.csv` if it recurs across games — classes, feats,
   conditions belong in general; proper nouns belong in the game file).
2. **TRANSLITERATE** — proper nouns (people, places, deities): render
   phonetically in Arabic script, e.g. `Terendelev → تيرنديليف`,
   `Kenabres → كينابرس`. Keep one spelling forever; note it below.
3. **SKIP** — ordinary English the MT already handles fine ("Perception
   improves", sentence fragments, UI verbs). Do not glossary what doesn't
   need pinning: every entry costs a pinning pass and a maintenance burden.

### Translation rules for ACCEPTed terms

- **Meaning over surface form.** Translate the *game sense*, not the common
  English sense. The canonical failure: `Cavalier` is the knight class →
  `فارس`, never `متعجرف` (the adjective "cavalier"). Same trap: `Order`
  (knightly order) → `رتبة`/`طائفة`, never `طلب` (a purchase order).
  The `sample_context` column exists to disambiguate — read it.
- **One term, one translation, everywhere.** Consistency beats elegance;
  a player must recognize the same ability every time they hear it.
- **Spoken, not read.** These terms are heard via TTS. Prefer renderings
  that are unambiguous *aloud*; avoid forms that depend on diacritics the
  listener can't see to disambiguate.
- **Established Arabic RPG/D&D conventions win** over invention when they
  exist (e.g. common community renderings of class names).
- **No markup, no placeholders** in either column. Plain text only.
- CSV hygiene: UTF-8, header `source,target`, no duplicate sources within
  one file (game file may deliberately override a general entry — that is
  the mechanism, not a duplicate).

### Human approval gate

An agent MAY fill in proposed targets, but rows enter `glossary.csv` only
after a human reviews them. Rationale: a wrong glossary entry is worse than
no entry — it gets confidently spoken on every occurrence. Log notable
decisions in the table below.

---

## Agent prompt (copy-paste when curating with Claude Code or similar)

> Read `glossary/games/<game>/candidates.csv`. For each row, using the
> `sample_context` to disambiguate meaning, classify it ACCEPT /
> TRANSLITERATE / SKIP per `glossary/general/references.md`. For ACCEPT and
> TRANSLITERATE rows, propose an Arabic target following the translation
> rules (game sense over common sense; one term one translation; must be
> clear when spoken aloud). Output a review table:
> `term | count | decision | proposed target | reasoning (one line)`.
> Do NOT write to any glossary.csv — a human merges approved rows.
> Flag any term whose context is insufficient to disambiguate.

---

## Decision log

| Term        | Decision      | Target      | Why / source                          |
|-------------|---------------|-------------|---------------------------------------|
| Cavalier    | ACCEPT        | فارس        | knight class, not the adjective       |
| Perception  | ACCEPT        | إدراك       | skill name, recurring rules term      |
| Terendelev  | TRANSLITERATE | تيرنديليف   | dragon (proper noun); fixed spelling  |

## Sources

- Game's own localization: `Wrath_Data/StreamingAssets/Localization/enGB.json`
  (authoritative for what terms exist and their in-game sense).
- Team decisions from the Trip localization report (rendering vs terminology
  axes; substitution-file precedent from XUnity.AutoTranslator).
