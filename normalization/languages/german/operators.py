import re

from normalization.constants.protectors import ordinal_placeholder
from normalization.languages.base import LanguageConfig, LanguageOperators
from normalization.languages.german.number_normalizer import GermanNumberNormalizer
from normalization.languages.german.ordinals import (
    CANONICAL_SUFFIX,
    ORDINAL_SUFFIXES,
    SPELLED_ORDINALS,
)
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
    digit_ordinal_suffixes=ORDINAL_SUFFIXES,
    canonical_ordinal_suffix=CANONICAL_SUFFIX,
    spelled_ordinals=SPELLED_ORDINALS,
)


# A period before a space or the end of the text, hidden from alpha2digit during
# expand_written_numbers_protecting_ordinals. The space keeps the word before it whole.
_RE_SENTENCE_PERIOD = re.compile(r"\.(?=\s|$)")
_HIDDEN_PERIOD = " \u01c2"
_RE_WRITTEN_ORDINAL = re.compile(r"(?<![\w.,])(\d+)\.(?!\d)")


@register_language
class GermanOperators(LanguageOperators):
    def __init__(self):
        super().__init__(GERMAN_CONFIG)
        self._number_normalizer = GermanNumberNormalizer()

    def get_word_replacements(self) -> dict[str, str]:
        return GERMAN_REPLACEMENTS

    def expand_written_numbers(self, text: str) -> str:
        return self._number_normalizer(text)

    def expand_written_numbers_protecting_ordinals(self, text: str) -> str:
        """Like expand_written_numbers, with each ordinal it reads as an ordinal placeholder.

        alpha2digit writes a spelled ordinal as "N." ("dritten" -> "3."), like a
        cardinal before a period ("drei." -> "3."). Periods already in the text are
        hidden behind a spaced mark first, so every "N." alpha2digit writes is an
        ordinal; the marks are put back as periods afterwards, apart from a number before
        them.
        """
        text = _RE_SENTENCE_PERIOD.sub(_HIDDEN_PERIOD, text)
        text = self._number_normalizer(text)
        text = _RE_WRITTEN_ORDINAL.sub(lambda m: ordinal_placeholder(m.group(1)), text)
        # A period back after a number ("drei." -> "3 .") is kept apart from it, so
        # protect_digit_ordinals does not read the cardinal as an ordinal.
        text = text.replace(_HIDDEN_PERIOD, " .")
        return re.sub(r"(?<=\D) \.", ".", text)
