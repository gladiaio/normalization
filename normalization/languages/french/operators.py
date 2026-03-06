from normalization.languages.base import (
    LanguageConfig,
    LanguageOperators,
)
from normalization.languages.registery import register_language

FRENCH_CONFIG = LanguageConfig(
    code="fr",
    decimal_separator=",",
    decimal_word="virgule",
    dot_word="point",
    thousand_separator=" ",
    currency_symbol_to_word={
        "€": "euros",
        "$": "dollars",
        "£": "livres",
        "¢": "cents",
        "¥": "yens",
    },
    at_word="arobase",
    percent_words=["pourcent", "pour cent"],
    greater_than_word="plus grand que",
    less_than_word="plus petit que",
    equals_word="égal à",
    degree_celsius_word="degrés celsius",
    degree_fahrenheit_word="degrés fahrenheit",
    filler_words=["euh", "hum", "beh", "bah", "ben", "hein"],
)


@register_language
class FrenchOperators(LanguageOperators):
    def __init__(self):
        super().__init__(FRENCH_CONFIG)
