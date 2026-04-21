"""Italian number normalizer using text2num's alpha2digit.

Converts spelled-out numbers to digits (e.g. venti → 20) and handles
mixed digit+word forms (e.g. 2 cento → due cento) before conversion
so alpha2digit does not misinterpret them.

A post-pass replaces words alpha2digit leaves unconverted in isolation:
- 'uno' → '1'
- 'due' → '2'
"""

import re

from text_to_num import alpha2digit

_RE_MIXED_NUMBER = re.compile(
    r"\b(\d+)\s+(cento|mila?|milioni?|miliardi?)\b",
    re.IGNORECASE,
)

_RE_UNO = re.compile(r"\buno\b", re.IGNORECASE)
_RE_DUE = re.compile(r"\bdue\b", re.IGNORECASE)


def _fix_remaining_words(text: str) -> str:
    """Replace number words alpha2digit did not convert."""
    text = _RE_UNO.sub("1", text)
    text = _RE_DUE.sub("2", text)
    return text


class ItalianNumberNormalizer:
    """Convert Italian spelled-out numbers to digits via text2num.alpha2digit.

    Accepts digit_words (word→digit mapping from LanguageConfig) to derive
    the digit→word mapping used for mixed-form pre-passes (e.g. '2 cento' → 'due cento').
    """

    def __init__(self, digit_words: dict[str, str]) -> None:
        self._digit_to_word = {v: k for k, v in digit_words.items()}

    def _normalize_mixed_numbers(self, text: str) -> str:
        """Convert '2 cento' → 'due cento' so alpha2digit yields 200, not '2 100'."""

        def replace(match: re.Match) -> str:
            number = match.group(1)
            multiplier = match.group(2)
            if len(number) == 1 and number in self._digit_to_word:
                return f"{self._digit_to_word[number]} {multiplier}"
            return match.group(0)

        return _RE_MIXED_NUMBER.sub(replace, text)

    def __call__(self, text: str) -> str:
        text = self._normalize_mixed_numbers(text)
        text = alpha2digit(text, "it")
        text = _fix_remaining_words(text)
        return text
