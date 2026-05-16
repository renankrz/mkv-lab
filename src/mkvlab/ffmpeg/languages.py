"""
Language code catalog used to match `language` tags reported by ffprobe.

Conventions
-----------
- Codes are stored lower-cased; matching is case-insensitive.
- Brazilian Portuguese (``pt-br``) and European Portuguese (``pt``) are kept in
  *disjoint* sets so callers can prefer ``pt-br`` first and fall back to ``pt``
  without ambiguity.
- The public helpers expose the language *keys* (``"pt-br"``, ``"pt"``,
  ``"en"``, ``"jp"``) — never raw ISO codes — so the rest of the codebase
  speaks a single vocabulary.
"""

from __future__ import annotations

from typing import Iterable

# --------------------------------------------------------------------------- #
# Language code sets
# --------------------------------------------------------------------------- #

# Brazilian Portuguese — explicit regional variants only (no overlap with `pt`).
PT_BR_CODES: frozenset[str] = frozenset(
    {
        "pt-br",
        "pt_br",
        "ptbr",
        "pob",
        "por-br",
        "por_br",
        "porbr",
        "bra",
        "brasil",
        "brazil",
    }
)

# European / generic Portuguese — kept *separate* from PT-BR on purpose.
PT_PT_CODES: frozenset[str] = frozenset(
    {
        "pt",
        "por",
        "portuguese",
    }
)

EN_CODES: frozenset[str] = frozenset(
    {
        "en",
        "eng",
        "english",
        "en-us",
        "en_us",
        "enus",
        "en-gb",
        "en_gb",
        "engb",
    }
)

JP_CODES: frozenset[str] = frozenset(
    {
        "jp",
        "jpn",
        "japanese",
        "ja",
        "jap",
    }
)

# Public registry. Keys are the canonical language identifiers used across
# the codebase and CLI flags. Order is irrelevant.
LANGUAGE_CODES: dict[str, frozenset[str]] = {
    "pt-br": PT_BR_CODES,
    "pt": PT_PT_CODES,
    "en": EN_CODES,
    "jp": JP_CODES,
}

# Canonical IETF-like tags written into output containers via
# `-metadata language=<value>`. Keep these conservative and widely supported.
CANONICAL_TAGS: dict[str, str] = {
    "pt-br": "pob",
    "pt": "por",
    "en": "eng",
    "jp": "jpn",
}


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #


def normalize_code(raw: str | None) -> str:
    """Return a lower-cased, trimmed language code (``""`` if ``raw`` is None)."""
    if not raw:
        return ""
    return raw.strip().lower()


def matches_language(raw: str | None, language: str) -> bool:
    """Return ``True`` when ``raw`` (an ffprobe ``language`` tag) belongs to ``language``."""
    if language not in LANGUAGE_CODES:
        raise ValueError(f"Unknown language key: {language!r}")
    return normalize_code(raw) in LANGUAGE_CODES[language]


def matches_any(raw: str | None, languages: Iterable[str]) -> bool:
    """Return ``True`` when ``raw`` matches any of the given language keys."""
    return any(matches_language(raw, lang) for lang in languages)


def canonical_tag(language: str) -> str:
    """Return the ISO 639-2 tag to write into output containers for ``language``."""
    try:
        return CANONICAL_TAGS[language]
    except KeyError as exc:
        raise ValueError(f"Unknown language key: {language!r}") from exc
