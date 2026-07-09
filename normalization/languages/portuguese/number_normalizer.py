"""Portuguese number normalizer using text2num's alpha2digit.

Converts spelled-out numbers to digits (e.g. vinte e tres → 23) and handles
mixed digit+word forms (e.g. 3 milhoes → tres milhoes) before conversion.
"""

import re

from text_to_num import alpha2digit

_RE_MIXED_NUMBER = re.compile(
    r"\b(\d+)\s+(mil|milhao|milhoes|milhão|milhões|bilhao|bilhoes|bilhão|bilhões)\b",
    re.IGNORECASE,
)

_RE_UM = re.compile(r"\bum\b", re.IGNORECASE)
_RE_DOIS = re.compile(r"\bdois\b", re.IGNORECASE)

# text2num expects accented Portuguese forms; STT often drops accents.
_UNACCENTED_NUMBER_FORMS: dict[str, str] = {
    "milhoes": "milhões",
    "milhao": "milhão",
    "bilhoes": "bilhões",
    "bilhao": "bilhão",
    "tres": "três",
    "seis": "seis",
}


def _restore_number_accents(text: str) -> str:
    for unaccented, canonical in _UNACCENTED_NUMBER_FORMS.items():
        text = re.sub(rf"\b{unaccented}\b", canonical, text, flags=re.IGNORECASE)
    return text


def _fix_remaining_words(text: str) -> str:
    """Replace number words alpha2digit did not convert."""
    text = _RE_UM.sub("1", text)
    text = _RE_DOIS.sub("2", text)
    return text


class PortugueseNumberNormalizer:
    """Convert Portuguese spelled-out numbers to digits via text2num.alpha2digit."""

    def __init__(self, digit_words: dict[str, str]) -> None:
        self._digit_to_word = {v: k for k, v in digit_words.items()}

    def _normalize_mixed_numbers(self, text: str) -> str:
        """Convert ``3 milhoes`` → ``tres milhoes`` so alpha2digit yields 3000000."""

        def replace(match: re.Match[str]) -> str:
            number = match.group(1)
            multiplier = match.group(2)
            if len(number) == 1 and number in self._digit_to_word:
                return f"{self._digit_to_word[number]} {multiplier}"
            return match.group(0)

        return _RE_MIXED_NUMBER.sub(replace, text)

    def __call__(self, text: str) -> str:
        text = _restore_number_accents(text)
        text = self._normalize_mixed_numbers(text)
        text = alpha2digit(text, "pt")
        text = _fix_remaining_words(text)
        return text
