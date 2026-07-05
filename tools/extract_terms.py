"""Offline glossary-candidate extractor. NEVER called from the runtime path.

Mines a game's text dump for capitalized terms/phrases that are glossary
candidates, ranks them by frequency, and writes
`glossary/games/<game>/candidates.csv` (term,count,context) for human/agent
curation. Schema-agnostic: walks any JSON recursively (works on WotR's
`Wrath_Data/StreamingAssets/Localization/enGB.json`) or plain TXT dumps.

Usage:
    python tools/extract_terms.py enGB.json --game pathfinder-wotr
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
from collections import Counter

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GLOSSARY_ROOT = os.path.join(REPO_ROOT, "glossary")

# Inline markup found in game string tables: {g|Encyclopedia:X}, <color=...>,
# [MORE]. Stripped before term detection so markup never leaks into terms.
_MARKUP = re.compile(r"\{[^{}]*\}|<[^<>]*>|\[[^\[\]]*\]")

# A capitalized phrase: one or more Capitalized words, optionally joined by
# lowercase connectors ("of", "the", "of the"), e.g. "Order of the Cavalier",
# "Melee Combat", "Terendelev". Hyphenated capitals ("Worldwound-touched")
# count as one word.
_CONNECTOR = r"(?:of|the|of\s+the)"
_CAPWORD = r"[A-Z][a-zA-Z'\-]+"
_PHRASE = re.compile(rf"\b{_CAPWORD}(?:\s+(?:{_CONNECTOR}\s+)?{_CAPWORD})*\b")

# Sentence-leading words that are only capitalized because of position.
_STOPWORDS = {
    "a", "an", "the", "and", "but", "or", "so", "if", "when", "while", "you",
    "your", "yours", "i", "we", "he", "she", "it", "they", "them", "this",
    "that", "these", "those", "there", "here", "what", "who", "why", "how",
    "where", "which", "not", "no", "yes", "do", "does", "did", "is", "are",
    "was", "were", "be", "been", "will", "would", "can", "could", "should",
    "may", "might", "must", "let", "then", "now", "well", "oh", "ah", "hey",
    "as", "at", "by", "for", "from", "in", "into", "of", "on", "to", "with",
    "my", "me", "his", "her", "its", "our", "their", "us", "him", "all",
    "some", "any", "each", "every", "one", "two", "three", "first", "come",
    "go", "get", "look", "see", "tell", "say", "perhaps", "maybe", "even",
    "still", "just", "only", "very", "too", "more", "most", "such", "many",
}


def iter_strings(node: object) -> "list[str]":
    """Yield every string value in an arbitrarily nested JSON structure."""
    out: list[str] = []
    stack = [node]
    while stack:
        current = stack.pop()
        if isinstance(current, str):
            out.append(current)
        elif isinstance(current, dict):
            stack.extend(current.values())
        elif isinstance(current, list):
            stack.extend(current)
    return out


def load_texts(path: str) -> "list[str]":
    """Load a JSON string table (any schema) or a plain-text dump."""
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        raw = f.read()
    if path.lower().endswith(".json"):
        return iter_strings(json.loads(raw))
    return [line for line in raw.splitlines() if line.strip()]


def strip_markup(text: str) -> str:
    # Apply repeatedly so nested markup ({outer {inner}}) fully unwraps.
    previous = None
    while previous != text:
        previous = text
        text = _MARKUP.sub(" ", text)
    return text


def normalize_term(term: str) -> str:
    """Collapse whitespace and drop leading/trailing articles/connectors."""
    words = term.split()
    while words and words[0].lower() in ("the", "a", "an"):
        words = words[1:]
    while words and words[-1].lower() in ("of", "the", "a", "an"):
        words = words[:-1]
    return " ".join(words)


def existing_glossary_terms(game: str) -> "set[str]":
    """Lowercased source terms already in the general + game glossaries."""
    known: set[str] = set()
    paths = [
        os.path.join(GLOSSARY_ROOT, "general", "glossary.csv"),
        os.path.join(GLOSSARY_ROOT, "games", game, "glossary.csv"),
    ]
    for path in paths:
        if not os.path.isfile(path):
            continue
        with open(path, "r", encoding="utf-8", newline="") as f:
            for row in csv.DictReader(f):
                source = (row.get("source") or "").strip()
                if source:
                    known.add(source.lower())
    return known


def extract(texts: "list[str]", known: "set[str]") -> "tuple[Counter, dict[str, str]]":
    counts: Counter = Counter()
    contexts: dict[str, str] = {}
    for text in texts:
        clean = strip_markup(text)
        for match in _PHRASE.finditer(clean):
            term = normalize_term(match.group())
            if not term or term.lower() in known:
                continue
            # Single stopword ("The", "Perhaps") or single letter: positional
            # capitalization, not a term.
            if " " not in term and (term.lower() in _STOPWORDS or len(term) < 3):
                continue
            counts[term] += 1
            if term not in contexts:
                snippet = " ".join(clean.split())
                contexts[term] = snippet[:200]
    return counts, contexts


def main(argv: "list[str] | None" = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("input", help="JSON string table or TXT dump to mine")
    parser.add_argument("--game", required=True,
                        help="game folder name under glossary/games/")
    parser.add_argument("--min-count", type=int, default=2,
                        help="drop terms seen fewer than this many times (default 2)")
    args = parser.parse_args(argv)

    texts = load_texts(args.input)
    known = existing_glossary_terms(args.game)
    counts, contexts = extract(texts, known)

    out_dir = os.path.join(GLOSSARY_ROOT, "games", args.game)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "candidates.csv")

    kept = [(term, count) for term, count in counts.most_common()
            if count >= args.min_count]
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["term", "count", "context"])
        for term, count in kept:
            writer.writerow([term, count, contexts[term]])

    print(f"{len(kept)} candidates ({len(counts)} raw terms, "
          f"{len(known)} already in glossaries) -> {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
