import re


def pin(text: str, glossary: dict[str, str]) -> tuple[str, dict[str, str]]:
    """Replace glossary terms in `text` with pass-through placeholders.

    Longest terms are matched first so e.g. "Melee Combat" wins over the
    substring "Combat". Matching is case-insensitive and word-boundary
    anchored. Returns the pinned text and a placeholder -> Arabic target
    mapping for `restore`.
    """
    if not glossary:
        return text, {}

    terms = sorted(glossary.keys(), key=len, reverse=True)
    pattern = re.compile(
        r"\b(" + "|".join(re.escape(term) for term in terms) + r")\b",
        re.IGNORECASE,
    )

    mapping: dict[str, str] = {}
    counter = 0

    def _replace(match: re.Match) -> str:
        nonlocal counter
        counter += 1
        placeholder = f"⟦T{counter}⟧"
        mapping[placeholder] = glossary[match.group(0).lower()]
        return placeholder

    pinned = pattern.sub(_replace, text)
    return pinned, mapping


def restore(translated_text: str, mapping: dict[str, str]) -> str:
    """Replace pinned placeholders with their Arabic targets.

    Tolerant to spacing/case mangling a machine translator may introduce
    around the placeholder brackets.
    """
    result = translated_text
    for placeholder, target in mapping.items():
        number = placeholder[2:-1]
        tolerant = re.compile(
            r"⟦\s*T\s*" + re.escape(number) + r"\s*⟧", re.IGNORECASE
        )
        result, count = tolerant.subn(target, result)
        if count == 0:
            print(f"[pinning] placeholder {placeholder} failed to restore")
    return result
