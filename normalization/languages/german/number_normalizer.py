"""German number normalizer using text2num's alpha2digit.

Converts spelled-out numbers to digits (e.g. zwanzig → 20) and handles
mixed digit+word forms (e.g. 2 hundert → zwei hundert) before conversion
so alpha2digit does not misinterpret them.

A post-pass replaces words alpha2digit leaves unconverted in isolation:
- 'null' → '0' (alpha2digit skips it standalone)
- 'zwei' → '2' (alpha2digit skips it standalone and in plain noun phrases)
'ein'/'eins' are intentionally excluded — 'ein' is the German indefinite
article and cannot be safely replaced without context.
"""

import re

from text_to_num import alpha2digit

_DIGIT_TO_GERMAN: dict[str, str] = {
    "0": "null",
    "1": "ein",
    "2": "zwei",
    "3": "drei",
    "4": "vier",
    "5": "fünf",
    "6": "sechs",
    "7": "sieben",
    "8": "acht",
    "9": "neun",
}

_RE_MIXED_NUMBER = re.compile(
    r"\b(\d+)\s+(hundert|tausend|millionen?|milliarden?|billionen?)\b",
    re.IGNORECASE,
)

_RE_ZWEI = re.compile(r"\bzwei\b", re.IGNORECASE)
_RE_NULL = re.compile(r"\bnull\b", re.IGNORECASE)


def _normalize_mixed_numbers(text: str) -> str:
    """Convert '2 hundert' → 'zwei hundert' so alpha2digit yields 200, not '2 100'."""

    def replace(match: re.Match) -> str:
        number = match.group(1)
        multiplier = match.group(2)
        if len(number) == 1 and number in _DIGIT_TO_GERMAN:
            return f"{_DIGIT_TO_GERMAN[number]} {multiplier}"
        return match.group(0)

    return _RE_MIXED_NUMBER.sub(replace, text)


def _fix_remaining_words(text: str) -> str:
    """Replace number words alpha2digit did not convert."""
    text = _RE_ZWEI.sub("2", text)
    text = _RE_NULL.sub("0", text)
    return text


class GermanNumberNormalizer:
    """Convert German spelled-out numbers to digits via text2num.alpha2digit."""

    def __call__(self, text: str) -> str:
        text = _normalize_mixed_numbers(text)
        text = alpha2digit(text, "de")
        text = _fix_remaining_words(text)
        return text
