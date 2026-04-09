import re

from normalization.languages.base import LanguageOperators
from normalization.steps.base import TextStep
from normalization.steps.registry import register_step


def _make_standalone_patterns(
    symbols: frozenset[str],
) -> tuple[re.Pattern, re.Pattern, re.Pattern, re.Pattern]:
    char_class = "[" + re.escape("".join(symbols)) + "]"
    between = re.compile(rf"([^0-9]){char_class}([^0-9])")
    start = re.compile(rf"^{char_class}([^0-9])")
    end = re.compile(rf"([^0-9]){char_class}$")
    standalone = re.compile(rf"^{char_class}$")
    return between, start, end, standalone


@register_step
class RemoveStandaloneCurrencySymbolsStep(TextStep):
    """Remove currency symbols that are not adjacent to numbers."""

    name = "remove_standalone_currency_symbols"

    def __call__(self, text: str, operators: LanguageOperators) -> str:
        symbols = frozenset(operators.config.currency_symbol_to_word.keys())
        if not symbols:
            return text

        between, start, end, standalone = _make_standalone_patterns(symbols)
        text = between.sub(r"\1 \2", text)
        text = start.sub(r" \1", text)
        text = end.sub(r"\1 ", text)
        text = standalone.sub(" ", text)
        return text
