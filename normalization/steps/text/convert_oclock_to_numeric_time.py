import re

from normalization.languages.base import LanguageOperators
from normalization.steps.base import TextStep
from normalization.steps.registry import register_step


@register_step
class ConvertOclockToNumericTimeStep(TextStep):
    """Convert 'ten o'clock' -> '10:00'.

    Reads operators.config.oclock_word and operators.config.time_words.
    Only processes time_words entries with numeric values 1-12. Values above 12 (minute expressions like "twenty", "thirty") are skipped because o'clock only applies to full hours.
    No operation when either field is None.
    """

    name = "convert_oclock_to_numeric_time"

    def __call__(self, text: str, operators: LanguageOperators) -> str:
        oclock_word = operators.config.oclock_word
        time_words = operators.config.time_words
        if oclock_word is None or time_words is None:
            # TODO: warn or log when oclock_word/time_words is not configured for this language
            return text
        for word, num in time_words.items():
            if int(num) > 12:
                continue  # skip minute-range values; only clock hours are valid for o'clock
            text = re.sub(
                rf"\b({word}|{num})\s+{re.escape(oclock_word)}\b",
                rf"{num}:00",
                text,
                flags=re.IGNORECASE,
            )
        return text
