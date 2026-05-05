import re

from normalization.constants import ProtectPlaceholder
from normalization.languages.base import LanguageOperators
from normalization.steps.base import TextStep
from normalization.steps.registry import register_step

_CURRENCY_NUM = rf"\d+(?:{ProtectPlaceholder.DECIMAL_SEPARATOR.value}\d+)?"


def _make_currency_patterns(
    symbol: str,
) -> tuple[re.Pattern[str], re.Pattern[str]]:
    escaped = re.escape(symbol)
    sym = rf"\b{escaped}\b" if len(symbol) > 1 else escaped
    before = re.compile(rf"{sym}\s*({_CURRENCY_NUM})", re.IGNORECASE)
    after = re.compile(rf"({_CURRENCY_NUM})\s*{sym}", re.IGNORECASE)
    return before, after


@register_step
class ReplaceCurrencyStep(TextStep):
    """Replace currency symbols with their corresponding words next to amounts.

    Reads ``operators.config.currency_symbol_to_word``. Multi-character symbols
    (e.g. ``kr``) are matched with word boundaries so amounts already written as
    ``… kronor`` are not parsed as ``… kr`` + ``onor``.
    """

    name = "replace_currency"

    def __call__(self, text: str, operators: LanguageOperators) -> str:
        for symbol, word in operators.config.currency_symbol_to_word.items():
            before, after = _make_currency_patterns(symbol)
            text = before.sub(rf"\1 {word}", text)
            text = after.sub(rf"\1 {word}", text)
        return text
