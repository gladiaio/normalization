from normalization.languages.base import LanguageConfig, LanguageOperators
from normalization.languages.german.replacements import GERMAN_REPLACEMENTS
from normalization.languages.german.sentence_replacements import (
    GERMAN_SENTENCE_REPLACEMENTS,
)
from normalization.languages.registry import register_language

GERMAN_CONFIG = LanguageConfig(
    code="de",
    decimal_separator=",",
    decimal_word="komma",
    thousand_separator=".",
    symbols_to_words={
        "@": "at",
        ".": "punkt",
        "+": "plus",
        "=": "gleich",
        ">": "größer als",
        "<": "kleiner als",
        "°": "grad",
        "°C": "grad celsius",
        "°F": "grad fahrenheit",
        "%": "prozent",
    },
    currency_symbol_to_word={
        "€": "euros",
        "$": "dollars",
        "£": "pounds",
        "¢": "cents",
        "¥": "yens",
    },
    filler_words=["äh", "ähm", "hm", "also", "naja", "halt"],
    sentence_replacements=GERMAN_SENTENCE_REPLACEMENTS,
)


@register_language
class GermanOperators(LanguageOperators):
    def __init__(self):
        super().__init__(GERMAN_CONFIG)

    def get_word_replacements(self) -> dict[str, str]:
        return GERMAN_REPLACEMENTS
