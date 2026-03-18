from normalization.languages.base import (
    LanguageConfig,
    LanguageOperators,
)
from normalization.languages.dutch.number_normalizer import DutchNumberNormalizer
from normalization.languages.registery import register_language

DUTCH_CONFIG = LanguageConfig(
    code="nl",
    decimal_separator=",",
    decimal_word="komma",
    thousand_separator=" ",
    symbols_to_words={
        "@": "apenstaartje",
        ".": "punt",
        "+": "plus",
        "=": "gelijk aan",
        ">": "groter dan",
        "<": "kleiner dan",
        "°": "graden",
        "°C": "graden celsius",
        "°F": "graden fahrenheit",
        "%": "procent",
    },
    currency_symbol_to_word={
        "€": "euros",
        "$": "dollars",
        "£": "ponden",
        "¢": "cent",
        "¥": "yens",
    },
    filler_words=["eh", "uh", "ehm", "hm", "hmm", "nou"],
)


@register_language
class DutchOperators(LanguageOperators):
    def __init__(self):
        super().__init__(DUTCH_CONFIG)
        self._number_normalizer = DutchNumberNormalizer()

    def expand_written_numbers(self, text: str) -> str:
        return self._number_normalizer(text)

    def get_word_replacements(self) -> dict[str, str]:
        from normalization.languages.dutch.replacements import DUTCH_REPLACEMENTS

        return DUTCH_REPLACEMENTS
