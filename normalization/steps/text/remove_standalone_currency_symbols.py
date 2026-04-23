import re

from normalization.languages.base import LanguageOperators
from normalization.steps.base import TextStep
from normalization.steps.registry import register_step


def _make_standalone_patterns(
    symbols: frozenset[str],
) -> tuple[re.Pattern[str], re.Pattern[str], re.Pattern[str], re.Pattern[str]]:
    """Build matchers for single-character currency symbols only.

    Multi-character symbols (e.g. ``kr``) must not be concatenated into a
    character class: that would treat each letter as its own symbol and strip
    ``k``/``r`` from ordinary words such as ``kronor`` or ``euros``.
    """
    char_class = "[" + re.escape("".join(symbols)) + "]"
    between = re.compile(rf"([^0-9]){char_class}([^0-9])")
    start = re.compile(rf"^{char_class}([^0-9])")
    end = re.compile(rf"([^0-9]){char_class}$")
    standalone = re.compile(rf"^{char_class}$")
    return between, start, end, standalone


def _strip_standalone_multi_char_symbol(text: str, symbol: str) -> str:
    """Remove ``symbol`` only when it forms its own token (not a prefix like ``kr`` in ``kronor``)."""
    esc = re.escape(symbol)
    return re.sub(rf"\b{esc}\b", " ", text, flags=re.IGNORECASE)


@register_step
class RemoveStandaloneCurrencySymbolsStep(TextStep):
    """Remove currency symbols that are not adjacent to numbers.

    Single-character symbols use the between/start/end patterns. Each
    multi-character key (e.g. ``kr``) is stripped only when it appears as its own
    token (``\\b...\\b``), so it is not confused with a substring inside a word.
    """

    name = "remove_standalone_currency_symbols"

    def __call__(self, text: str, operators: LanguageOperators) -> str:
        symbols = frozenset(operators.config.currency_symbol_to_word.keys())
        if not symbols:
            return text

        singles = frozenset(s for s in symbols if len(s) == 1)
        if singles:
            between, start, end, standalone = _make_standalone_patterns(singles)
            text = between.sub(r"\1 \2", text)
            text = start.sub(r" \1", text)
            text = end.sub(r"\1 ", text)
            text = standalone.sub(" ", text)

        multi_symbols: list[str] = [s for s in symbols if len(s) > 1]
        for sym in sorted(multi_symbols, key=lambda s: len(s), reverse=True):
            text = _strip_standalone_multi_char_symbol(text, sym)
        return text
