"""Merge hyphenated Portuguese clitic pronouns into single tokens for WER scoring.

Oral Portuguese often attaches clitics to imperatives (``envie-me`` / ``enviame``).
ASR may hyphenate or space them; this step canonicalizes to the glued form.
"""

import re

_CLITIC_SUFFIXES = (
    "me",
    "te",
    "se",
    "lo",
    "la",
    "lhe",
    "lhes",
    "nos",
    "vos",
    "los",
    "las",
    "no",
    "na",
    "lho",
    "lha",
    "lhes",
)

_RE_HYPHEN_CLITIC = re.compile(
    rf"\b(\w+)-({'|'.join(_CLITIC_SUFFIXES)})\b",
    re.IGNORECASE,
)


def merge_hyphenated_clitics(text: str) -> str:
    """``digame-me`` / ``diga-me`` → ``digame``."""
    return _RE_HYPHEN_CLITIC.sub(
        lambda m: m.group(1).lower() + m.group(2).lower(), text
    )
