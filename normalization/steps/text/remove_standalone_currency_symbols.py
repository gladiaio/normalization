import re

from normalization.languages.base import LanguageOperators
from normalization.steps.base import TextStep
from normalization.steps.registery import register_step

_RE_CURRENCY_BETWEEN = re.compile(r"([^0-9])[€$£¥¢%]([^0-9])")
_RE_CURRENCY_START = re.compile(r"^[€$£¥¢%]([^0-9])")
_RE_CURRENCY_END = re.compile(r"([^0-9])[€$£¥¢%]$")
_RE_CURRENCY_STANDALONE = re.compile(r"^[€$£¥¢%]$")


@register_step
class RemoveStandaloneCurrencySymbolsStep(TextStep):
    """Remove currency/percent symbols that are not adjacent to numbers."""

    name = "remove_standalone_currency_symbols"

    def __call__(self, text: str, operators: LanguageOperators) -> str:
        text = _RE_CURRENCY_BETWEEN.sub(r"\1 \2", text)
        text = _RE_CURRENCY_START.sub(r" \1", text)
        text = _RE_CURRENCY_END.sub(r"\1 ", text)
        text = _RE_CURRENCY_STANDALONE.sub(" ", text)
        return text
