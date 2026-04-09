import re

from normalization.constants.protectors import ProtectPlaceholder
from normalization.languages.base import LanguageOperators
from normalization.steps.base import TextStep
from normalization.steps.registry import register_step

_PROTECTION_MARKERS = [
    ProtectPlaceholder.DECIMAL_SEPARATOR.value,
    ProtectPlaceholder.EMAIL_AT.value,
    ProtectPlaceholder.EMAIL_DOT.value,
    ProtectPlaceholder.PHONE_PLUS.value,
]


@register_step
class ExpandAlphanumericCodesStep(TextStep):
    """Space out uppercase words and alphanumeric codes.

    'ABC123' -> 'A B C 1 2 3', 'CNN' -> 'C N N'.
    Skips pure numbers, ordinals (1st, 2nd), and protection markers. Must run before casefold_text.
    """

    name = "expand_alphanumeric_codes"

    def __call__(self, text: str, operators: LanguageOperators) -> str:
        ordinal_suffixes = operators.config.ordinal_suffixes
        if ordinal_suffixes:
            suffix_pattern = re.compile(
                r"^\d+(" + "|".join(re.escape(s) for s in ordinal_suffixes) + r")$",
                re.IGNORECASE,
            )
        else:
            suffix_pattern = None

        def _expand_word(match: re.Match) -> str:
            word = match.group(0)
            has_digit = any(c.isdigit() for c in word)
            if word.isupper():
                return " ".join(word)
            if has_digit:
                return " ".join(word.upper())
            return word

        def _should_process(match: re.Match) -> str:
            word = match.group(0)

            if word.isdigit():
                return word

            if suffix_pattern and suffix_pattern.match(word):
                return word

            word_upper = word.upper()
            if any(marker in word_upper for marker in _PROTECTION_MARKERS):
                return word

            has_digit = any(c.isdigit() for c in word)
            if word.isupper() or has_digit:
                return _expand_word(match)

            return word

        return re.sub(r"\b[A-Za-z0-9]{2,}\b", _should_process, text)
