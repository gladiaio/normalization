import re

from normalization.languages.base import LanguageOperators
from normalization.steps.base import TextStep
from normalization.steps.registry import register_step

# British long-form numbers insert a comma after these scale words
# ("one thousand, two hundred"). Not a list separator.
_SCALE_WORDS_WITH_COMMA = ("thousand", "million", "billion", "trillion")


def _word_alternation(words: list[str]) -> str:
    sorted_words = sorted(words, key=lambda w: len(w), reverse=True)
    return "|".join(re.escape(w) for w in sorted_words)


@register_step
class NormalizePunctuationBetweenNumberWordsStep(TextStep):
    """Normalize punctuation between spelled number words.

    - Hyphens between any number_words: 'ninety-nine' -> 'ninety nine',
      'two-one-three' -> 'two one three'.
    - Commas after scale words: 'thousand, two' -> 'thousand two' (British
      long form).
    - Commas / dots / ellipsis / Arabic comma only between digit_words (0-9):
      'seven, zero' -> 'seven zero'. Tens like 'sixty, seventy' keep their
      comma so expand + list-comma protect yield '60 70', not '6070'.

    Falls back to number_words for the digit comma/dot class when digit_words
    is unset. No-op when number_words is empty.
    """

    name = "normalize_punctuation_between_number_words"

    def __call__(self, text: str, operators: LanguageOperators) -> str:
        number_words = operators.config.number_words
        if not number_words:
            return text

        number_group = f"(?:{_word_alternation(list(number_words))})"
        # Compounds written with a hyphen (ninety-nine, two-one-three).
        text = re.sub(
            rf"({number_group})\s*-\s*(?={number_group})",
            r"\1 ",
            text,
            flags=re.IGNORECASE,
        )

        scale_alt = "|".join(_SCALE_WORDS_WITH_COMMA)
        text = re.sub(
            rf"\b({scale_alt})\s*,\s*(?={number_group})",
            r"\1 ",
            text,
            flags=re.IGNORECASE,
        )

        digit_words = operators.config.digit_words
        comma_words = list(digit_words) if digit_words else list(number_words)
        if not comma_words:
            return text
        digit_group = f"(?:{_word_alternation(comma_words)})"
        # Include Arabic comma (U+060C) for digit-by-digit ASR.
        text = re.sub(
            rf"({digit_group})\s*[,.…\u060c]+\s*(?={digit_group})",
            r"\1 ",
            text,
            flags=re.IGNORECASE,
        )
        return text
