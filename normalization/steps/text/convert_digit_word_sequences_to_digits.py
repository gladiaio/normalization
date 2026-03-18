import re

from normalization.languages.base import LanguageOperators
from normalization.steps.base import TextStep
from normalization.steps.registry import register_step


@register_step
class ConvertDigitWordSequencesToDigitsStep(TextStep):
    """Convert sequences of 3+ digit words to actual digits.

    'two one three four' -> '2134', 'seven zero' stays (only 2 words).
    Delegates the word-to-digit mapping to operators.config.digit_words.
    """

    name = "convert_digit_word_sequences_to_digits"

    def __call__(self, text: str, operators: LanguageOperators) -> str:
        digit_words = operators.config.digit_words
        if not digit_words:
            return text

        # Sort longest first so alternation prefers longer matches (e.g. "oh" before "o")
        sorted_words = sorted(digit_words, key=lambda w: len(w), reverse=True)
        word_pattern = "|".join(re.escape(w) for w in sorted_words)
        pattern = (
            rf"\b(?:{word_pattern})"
            rf"(?:\s+(?:{word_pattern})){{2,}}\b"
        )

        def _convert(match: re.Match) -> str:
            words = match.group(0).lower().split()
            digits = []
            for word in words:
                if word in digit_words:
                    digits.append(digit_words[word])
                else:
                    return match.group(0)
            return "".join(digits)

        return re.sub(pattern, _convert, text, flags=re.IGNORECASE)
