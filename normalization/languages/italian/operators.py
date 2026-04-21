from normalization.languages.base import LanguageConfig, LanguageOperators
from normalization.languages.italian.number_normalizer import ItalianNumberNormalizer
from normalization.languages.italian.replacements import ITALIAN_REPLACEMENTS
from normalization.languages.italian.sentence_replacements import (
    ITALIAN_SENTENCE_REPLACEMENTS,
)
from normalization.languages.registry import register_language

# Single digits 1-9: shared by digit_words and any future time/compound helpers.
_ONE_TO_NINE: dict[str, str] = {
    "uno": "1",
    "due": "2",
    "tre": "3",
    "quattro": "4",
    "cinque": "5",
    "sei": "6",
    "sette": "7",
    "otto": "8",
    "nove": "9",
}

ITALIAN_CONFIG = LanguageConfig(
    code="it",
    decimal_separator=",",
    decimal_word="virgola",
    thousand_separator=".",
    symbols_to_words={
        "@": "chiocciola",
        ".": "punto",
        "+": "più",
        "=": "uguale a",
        ">": "maggiore di",
        "<": "minore di",
        "°": "grado",
        "°C": "gradi celsius",
        "°F": "gradi fahrenheit",
        "%": "percento",
    },
    currency_symbol_to_word={
        "€": "euro",
        "$": "dollari",
        "£": "sterline",
        "¢": "centesimi",
        "¥": "yen",
    },
    filler_words=[
        "eh",
        "ehm",
        "mm",
        "mh",
        "cioè",
        "cioe",
        "tipo",
        "insomma",
        "allora",
        "beh",
        "bah",
        "dunque",
        "magari",
        "praticamente",
    ],
    sentence_replacements=ITALIAN_SENTENCE_REPLACEMENTS,
    digit_words={"zero": "0", **_ONE_TO_NINE},
    number_words=[
        "zero",
        *_ONE_TO_NINE,
        "dieci",
        "undici",
        "dodici",
        "tredici",
        "quattordici",
        "quindici",
        "sedici",
        "diciassette",
        "diciotto",
        "diciannove",
        "venti",
        "trenta",
        "quaranta",
        "cinquanta",
        "sessanta",
        "settanta",
        "ottanta",
        "novanta",
        "cento",
        "mille",
        "mila",
        "milione",
        "milioni",
        "miliardo",
        "miliardi",
    ],
    plus_word="più",
)


@register_language
class ItalianOperators(LanguageOperators):
    def __init__(self):
        super().__init__(ITALIAN_CONFIG)
        self._number_normalizer = ItalianNumberNormalizer(
            ITALIAN_CONFIG.digit_words or {}
        )

    def get_word_replacements(self) -> dict[str, str]:
        return ITALIAN_REPLACEMENTS

    def expand_written_numbers(self, text: str) -> str:
        return self._number_normalizer(text)
