import re

from normalization.languages.base import LanguageOperators
from normalization.steps.base import TextStep
from normalization.steps.registery import register_step

_RE_DEGREE_CELSIUS = re.compile(r"(\d+)°C", re.IGNORECASE)
_RE_DEGREE_FAHRENHEIT = re.compile(r"(\d+)°F", re.IGNORECASE)


@register_step
class ConvertDegreeSymbolsToWordsStep(TextStep):
    """Convert °C and °F to language-specific words using language config from operators."""

    name = "convert_degree_symbols_to_words"

    def __call__(self, text: str, operators: LanguageOperators) -> str:
        cfg = operators.config
        text = _RE_DEGREE_CELSIUS.sub(rf"\1 {cfg.degree_celsius_word}", text)
        text = _RE_DEGREE_FAHRENHEIT.sub(rf"\1 {cfg.degree_fahrenheit_word}", text)
        return text
