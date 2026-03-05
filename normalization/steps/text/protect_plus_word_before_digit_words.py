import re

from normalization.constants.protectors import ProtectPlaceholder
from normalization.languages.base import LanguageOperators
from normalization.steps.base import TextStep
from normalization.steps.registery import register_step


@register_step
class ProtectPlusWordBeforeDigitWordsStep(TextStep):
    """Convert the plus word to XPLUSX before digit words (phone number context).

    Reads operators.config.plus_word and operators.config.digit_words.
    No-op when plus_word is None or digit_words is empty/None.
    """

    name = "protect_plus_word_before_digit_words"

    def __call__(self, text: str, operators: LanguageOperators) -> str:
        plus_word = operators.config.plus_word
        if plus_word is None:
            return text

        digit_words = operators.config.digit_words
        if not digit_words:
            return text

        placeholder = ProtectPlaceholder.PHONE_PLUS.value
        sorted_words = sorted(digit_words, key=lambda w: len(w), reverse=True)
        word_alts = "|".join(re.escape(w) for w in sorted_words)
        lookahead = rf"(?=(?:{word_alts}|\d))"
        return re.sub(
            rf"\b{re.escape(plus_word)}\s+{lookahead}",
            f"{placeholder} ",
            text,
            flags=re.IGNORECASE,
        )
