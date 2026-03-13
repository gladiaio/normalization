import re

from normalization.languages.base import LanguageOperators
from normalization.steps.base import TextStep
from normalization.steps.registery import register_step

_RE_DEGREE_CELSIUS = re.compile(r"(\d+)°C", re.IGNORECASE)
_RE_DEGREE_FAHRENHEIT = re.compile(r"(\d+)°F", re.IGNORECASE)
_RE_DEGREE = re.compile(r"(\d+)°", re.IGNORECASE)


@register_step
class ConvertDegreeSymbolsToWordsStep(TextStep):
    """Convert °C and °F to language-specific words using language config from operators."""

    name = "convert_degree_symbols_to_words"

    def __call__(self, text: str, operators: LanguageOperators) -> str:
        stw = operators.config.symbols_to_words
        if "°C" in stw:
            text = _RE_DEGREE_CELSIUS.sub(rf"\1 {stw['°C']}", text)
        if "°F" in stw:
            text = _RE_DEGREE_FAHRENHEIT.sub(rf"\1 {stw['°F']}", text)
        if "°" in stw:
            text = _RE_DEGREE.sub(rf"\1 {stw['°']}", text)
        return text
