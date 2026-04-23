import re

from normalization.languages.base import LanguageOperators
from normalization.steps.base import TextStep
from normalization.steps.registry import register_step


def _currency_touching_digit(text: str, start: int, end: int) -> bool:
    """True if a digit is next to this span, allowing only whitespace in between."""
    i = start - 1
    while i >= 0 and text[i].isspace():
        i -= 1
    if i >= 0 and text[i].isdigit():
        return True
    i = end
    while i < len(text) and text[i].isspace():
        i += 1
    if i < len(text) and text[i].isdigit():
        return True
    return False


def _make_single_char_patterns(
    symbols: frozenset[str],
) -> tuple[re.Pattern[str], re.Pattern[str], re.Pattern[str], re.Pattern[str]]:
    char_class = "[" + re.escape("".join(symbols)) + "]"
    between = re.compile(rf"([^0-9]){char_class}([^0-9])")
    start = re.compile(rf"^{char_class}([^0-9])")
    end = re.compile(rf"([^0-9]){char_class}$")
    standalone = re.compile(rf"^{char_class}$")
    return between, start, end, standalone


@register_step
class RemoveStandaloneCurrencySymbolsStep(TextStep):
    """Remove currency symbols that are not adjacent to numbers.

    Single-character symbols use the classic between/start/end patterns (not
    between two digits). Multi-character keys (e.g. ``kr``) are matched only as
    whole tokens (``\\b...\\b``) and are skipped when a digit is nearby with
    only whitespace in between, so ordinary words are not corrupted.
    """

    name = "remove_standalone_currency_symbols"

    def __call__(self, text: str, operators: LanguageOperators) -> str:
        symbols = tuple(operators.config.currency_symbol_to_word.keys())
        if not symbols:
            return text

        singles = frozenset(s for s in symbols if len(s) == 1)

        for sym in sorted(
            (s for s in symbols if len(s) > 1),
            key=len,
            reverse=True,
        ):
            esc = re.escape(str(sym))
            pat = re.compile(rf"\b{esc}\b", re.IGNORECASE)
            cur_text = text

            def repl(m: re.Match[str]) -> str:
                if _currency_touching_digit(cur_text, m.start(), m.end()):
                    return m.group(0)
                return ""

            text = pat.sub(repl, cur_text)

        if singles:
            between, start, end, standalone = _make_single_char_patterns(singles)
            text = between.sub(r"\1 \2", text)
            text = start.sub(r" \1", text)
            text = end.sub(r"\1 ", text)
            text = standalone.sub(" ", text)

        return text
