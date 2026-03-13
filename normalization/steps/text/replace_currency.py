import re

from normalization.constants import ProtectPlaceholder
from normalization.languages.base import LanguageOperators
from normalization.steps.base import TextStep
from normalization.steps.registery import register_step

_CURRENCY_NUM = rf"\d+(?:{ProtectPlaceholder.DECIMAL_SEPARATOR.value}\d+)?"


def _make_currency_patterns(symbol: str) -> tuple[re.Pattern, re.Pattern]:
    escaped = re.escape(symbol)
    before = re.compile(rf"{escaped}\s*({_CURRENCY_NUM})", re.IGNORECASE)
    after = re.compile(rf"({_CURRENCY_NUM})\s*{escaped}", re.IGNORECASE)
    return before, after


@register_step
class ReplaceCurrencyStep(TextStep):
    """
    Replace currency symbols with their corresponding words.
    """

    name = "replace_currency"

    def __call__(self, text: str, operators: LanguageOperators) -> str:
        for symbol, word in operators.config.currency_symbol_to_word.items():
            before, after = _make_currency_patterns(symbol)
            text = before.sub(rf"\1 {word}", text)
            text = after.sub(rf"\1 {word}", text)
        return text
