"""Merge hyphenated Portuguese clitic pronouns into single tokens for WER scoring.

Oral Portuguese often attaches clitics to imperatives (``envie-me`` / ``enviame``).
ASR may hyphenate them; this step canonicalizes to the glued form without
breaking fixed compounds such as ``bem-te-vi``.
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
)

# Stems that form fixed compounds with ``-te`` (not imperative + clitic).
_TE_CLITIC_SKIP_STEMS = frozenset({"bem"})

_RE_HYPHEN_CLITIC = re.compile(
    rf"\b(\w+)-({'|'.join(_CLITIC_SUFFIXES)})\b",
    re.IGNORECASE,
)


def merge_hyphenated_clitics(text: str) -> str:
    """``envie-me`` / ``diga-me`` → ``enviame`` / ``digame``."""

    def _merge(match: re.Match[str]) -> str:
        stem, clitic = match.group(1), match.group(2)
        if clitic.lower() == "te" and stem.lower() in _TE_CLITIC_SKIP_STEMS:
            return match.group(0)
        return stem.lower() + clitic.lower()

    return _RE_HYPHEN_CLITIC.sub(_merge, text)
