import re

from normalization.languages.base import LanguageOperators
from normalization.steps.base import TextStep
from normalization.steps.registery import register_step


@register_step
class NormalizePunctuationBetweenNumberWordsStep(TextStep):
    """Replace commas, dots, hyphens between number words with a single space.

    Handles: 'seven, zero' -> 'seven zero', 'two-one-three' -> 'two one three'.
    Reads operators.config.number_words. No-op when None.
    """

    name = "normalize_punctuation_between_number_words"

    def __call__(self, text: str, operators: LanguageOperators) -> str:
        number_words = operators.config.number_words
        if not number_words:
            return text

        sorted_words = sorted(number_words, key=lambda w: len(w), reverse=True)
        alternation = "|".join(re.escape(w) for w in sorted_words)
        number_group = f"(?:{alternation})"
        pattern = re.compile(
            rf"({number_group})\s*[,.\-…]+\s*(?={number_group})",
            flags=re.IGNORECASE,
        )
        return pattern.sub(r"\1 ", text)
