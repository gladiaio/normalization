from normalization.languages.base import LanguageConfig, LanguageOperators
from normalization.languages.german.number_normalizer import GermanNumberNormalizer
from normalization.languages.german.replacements import GERMAN_REPLACEMENTS
from normalization.languages.german.sentence_replacements import (
    GERMAN_SENTENCE_REPLACEMENTS,
)
from normalization.languages.registry import register_language

_GERMAN_DIGIT_WORDS: dict[str, str] = {
    "null": "0",
    "ein": "1",
    "eins": "1",
    "zwei": "2",
    "drei": "3",
    "vier": "4",
    "fünf": "5",
    "sechs": "6",
    "sieben": "7",
    "acht": "8",
    "neun": "9",
}

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
    digit_words=_GERMAN_DIGIT_WORDS,
    number_words=[
        *_GERMAN_DIGIT_WORDS,
        "zehn",
        "elf",
        "zwölf",
        "dreizehn",
        "vierzehn",
        "fünfzehn",
        "sechzehn",
        "siebzehn",
        "achtzehn",
        "neunzehn",
        "zwanzig",
        "dreißig",
        "vierzig",
        "fünfzig",
        "sechzig",
        "siebzig",
        "achtzig",
        "neunzig",
        "hundert",
        "tausend",
        "million",
        "millionen",
        "milliarde",
        "milliarden",
        "billion",
        "billionen",
    ],
    plus_word="plus",
)


@register_language
class GermanOperators(LanguageOperators):
    def __init__(self):
        super().__init__(GERMAN_CONFIG)
        self._number_normalizer = GermanNumberNormalizer()

    def get_word_replacements(self) -> dict[str, str]:
        return GERMAN_REPLACEMENTS

    def expand_written_numbers(self, text: str) -> str:
        return self._number_normalizer(text)
