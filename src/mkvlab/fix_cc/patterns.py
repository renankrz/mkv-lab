"""Compiled regular expressions used by the cleaning steps.

Centralising the patterns avoids duplication and makes it easy to audit the
set of strings the cleaner recognises as CC/SDH noise.
"""

import re

# Pattern bodies — kept named so steps and analysis helpers reference them
# instead of re-compiling literals.

PARENTHESES = re.compile(r"\([^)]*\)")
BRACKETS = re.compile(r"\[[^\]]*\]")
CURLY_BRACKETS = re.compile(r"\{[^}]*\}")
HASH = re.compile(r"#[^#]*#")
MUSIC_SIGN = re.compile(r"♪")
DOUBLE_HYPHENS = re.compile(r"--")
LENGTHY_ELLIPSIS = re.compile(r"\.{4,}")
SPEAKER = re.compile(r"^\s*([^:\n]+?)\s*:", re.IGNORECASE)
LEADING_DASHES = re.compile(r"^[\-\–\—]")
MULTIPLE_SPACES = re.compile(r"\s+")
SPACES_BEFORE_PUNCTUATION = re.compile(r"\s+([.,!?;:])")
DASH_TRAILING_SPACE = re.compile(r"([\-\–\—])\s+")
