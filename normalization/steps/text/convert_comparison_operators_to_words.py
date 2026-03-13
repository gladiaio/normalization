import re

from normalization.languages.base import LanguageOperators
from normalization.steps.base import TextStep
from normalization.steps.registery import register_step

_RE_GREATER_THAN = re.compile(r"(\d+)\s*>\s*(\d+)")
_RE_LESS_THAN = re.compile(r"(\d+)\s*<\s*(\d+)")
_RE_EQUALS = re.compile(r"(\w+)\s*=\s*(\d+)")


@register_step
class ConvertComparisonOperatorsToWordsStep(TextStep):
    """Convert >, <, = to language-specific words in numeric contexts using language config from operators."""

    name = "convert_comparison_operators_to_words"

    def __call__(self, text: str, operators: LanguageOperators) -> str:
        stw = operators.config.symbols_to_words
        if ">" in stw:
            text = _RE_GREATER_THAN.sub(rf"\1 {stw['>']} \2", text)
        if "<" in stw:
            text = _RE_LESS_THAN.sub(rf"\1 {stw['<']} \2", text)
        if "=" in stw:
            text = _RE_EQUALS.sub(rf"\1 {stw['=']} \2", text)
        return text
