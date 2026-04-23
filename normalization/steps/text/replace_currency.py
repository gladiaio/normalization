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
    # Alphanumeric codes (e.g. "kr") must be whole tokens so we do not match
    # "kr" inside "kroner" after another step has already expanded the amount.
    if symbol.isalnum():
        before = re.compile(rf"\b{escaped}\b\s*({_CURRENCY_NUM})", re.IGNORECASE)
        after = re.compile(rf"({_CURRENCY_NUM})\s*\b{escaped}\b", re.IGNORECASE)
    else:
        before = re.compile(rf"{escaped}\s*({_CURRENCY_NUM})", re.IGNORECASE)
        after = re.compile(rf"({_CURRENCY_NUM})\s*{escaped}", re.IGNORECASE)
    return before, after


@register_step
class ReplaceCurrencyStep(TextStep):
    """Replace currency symbols with their corresponding words next to amounts.

    For each entry in ``operators.config.currency_symbol_to_word``, substitutes
    the symbol before or after a numeric literal (including placeholder decimals).
    Alphanumeric symbols (e.g. ``kr``) use word boundaries so a token like
    ``kroner`` is not treated as ``kr`` plus a suffix.
    """

    name = "replace_currency"

    def __call__(self, text: str, operators: LanguageOperators) -> str:
        for symbol, word in operators.config.currency_symbol_to_word.items():
            before, after = _make_currency_patterns(symbol)
            text = before.sub(rf"\1 {word}", text)
            text = after.sub(rf"\1 {word}", text)
        return text
