"""French number normalizer using text2num's alpha2digit.

Converts spelled-out numbers to digits (e.g. vingt trois → 23) and handles
mixed digit+word forms (e.g. 3 milliards → trois milliards) before conversion
so alpha2digit does not misinterpret them.
"""

import re

try:
    from text_to_num import alpha2digit
except ImportError:
    alpha2digit = None


# Digit-to-French word mapping for normalizing "3 milliards" → "trois milliards".
_DIGIT_TO_FRENCH: dict[str, str] = {
    "0": "zéro",
    "1": "un",
    "2": "deux",
    "3": "trois",
    "4": "quatre",
    "5": "cinq",
    "6": "six",
    "7": "sept",
    "8": "huit",
    "9": "neuf",
}

# Pattern: digit(s) followed by millions/milliards (French) or billions/trillions.
_RE_MIXED_NUMBER = re.compile(
    r"\b(\d+)\s+(millions?|milliards?|billions?|trillions?)\b",
    re.IGNORECASE,
)


def _normalize_mixed_numbers(text: str) -> str:
    """Convert '3 milliards' → 'trois milliards' so alpha2digit yields 3e9, not 31e9.

    alpha2digit may concatenate a lone digit with the following word; converting
    the digit to a word avoids that (e.g. 'trois milliards' → 3000000000).
    """

    def replace(match: re.Match) -> str:
        number = match.group(1)
        multiplier = match.group(2)
        if len(number) == 1 and number in _DIGIT_TO_FRENCH:
            return f"{_DIGIT_TO_FRENCH[number]} {multiplier}"
        # Multi-digit: keep as-is; alpha2digit will handle or leave unchanged
        return match.group(0)

    return _RE_MIXED_NUMBER.sub(replace, text)


class FrenchNumberNormalizer:
    """Convert French spelled-out numbers to digits via text2num.alpha2digit.

    Applies a pre-pass to normalize mixed digit+word forms (e.g. 3 milliards)
    before calling alpha2digit.
    """

    def __init__(self) -> None:
        if alpha2digit is None:
            raise ImportError(
                "French number normalization requires the text2num package. "
                "Install it with: uv add text2num"
            )
        self._alpha2digit = alpha2digit

    def __call__(self, text: str) -> str:
        text = _normalize_mixed_numbers(text)
        return self._alpha2digit(text, "fr")
