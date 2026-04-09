import re

from normalization.languages.base import LanguageOperators
from normalization.steps.base import TextStep
from normalization.steps.registry import register_step


@register_step
class FixDotAdjacentNumberWordsStep(TextStep):
    """Convert number words back to digits when adjacent to 'dot' (IPs/versions).

    'zero dot one dot two' -> '0 dot 1 dot 2'.
    Single-character entries (e.g. 'o') are excluded to avoid false positives
    in non-numeric contexts.
    """

    name = "fix_dot_adjacent_number_words"

    def __call__(self, text: str, operators: LanguageOperators) -> str:
        digit_words = operators.config.digit_words
        if not digit_words:
            return text

        dot_word = operators.config.symbols_to_words.get(".")
        if dot_word is None:
            return text
        # Skip single-char entries: standalone "o" is too ambiguous in dot contexts
        for word, digit in digit_words.items():
            if len(word) < 2:
                continue
            text = re.sub(
                rf"\b{re.escape(word)}\b(?=\s+{re.escape(dot_word)}\b)", digit, text
            )
            text = re.sub(
                rf"(?<=\b{re.escape(dot_word)}\s){re.escape(word)}\b", digit, text
            )
        return text
