import re

from normalization.languages.base import LanguageOperators
from normalization.steps.base import TextStep
from normalization.steps.registery import register_step


@register_step
class ConvertDecimalPeriodsToDecimalWordStep(TextStep):
    """Convert remaining decimal periods to the language decimal word, defined in language config from operators.

    '10.5' -> '10 point 5' (English).
    Avoids patterns already converted to 'dot' (IPs, versions).
    """

    name = "convert_decimal_periods_to_decimal_word"

    def __call__(self, text: str, operators: LanguageOperators) -> str:
        dot_word = operators.config.symbols_to_words.get(".")
        if dot_word is None:
            return text
        decimal_word = operators.config.decimal_word
        text = re.sub(
            rf"(?<!\d\s{re.escape(dot_word)}\s)(\d+)\.(\d+)(?!\s+{re.escape(dot_word)}\s+\d)",
            rf"\1 {decimal_word} \2",
            text,
        )
        return text
