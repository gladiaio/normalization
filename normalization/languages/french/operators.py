from normalization.languages.base import (
    LanguageConfig,
    LanguageOperators,
)
from normalization.languages.registry import register_language

FRENCH_CONFIG = LanguageConfig(
    code="fr",
    decimal_separator=",",
    decimal_word="virgule",
    thousand_separator=" ",
    symbols_to_words={
        "@": "arobase",
        ".": "point",
        "+": "plus",
        "=": "égal à",
        ">": "plus grand que",
        "<": "plus petit que",
        "°": "degré",
        "°C": "degrés celsius",
        "°F": "degrés fahrenheit",
        "%": "pourcent",
    },
    currency_symbol_to_word={
        "€": "euros",
        "$": "dollars",
        "£": "livres",
        "¢": "cents",
        "¥": "yens",
    },
    filler_words=["euh", "hum", "beh", "bah", "ben", "hein"],
)


@register_language
class FrenchOperators(LanguageOperators):
    def __init__(self):
        super().__init__(FRENCH_CONFIG)
