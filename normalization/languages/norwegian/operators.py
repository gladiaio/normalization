from normalization.languages.base import LanguageConfig, LanguageOperators
from normalization.languages.norwegian.number_normalizer import (
    NorwegianNumberNormalizer,
)
from normalization.languages.registry import register_language

_NORWEGIAN_DIGIT_WORDS: dict[str, str] = {
    "null": "0",
    "en": "1",
    "ett": "1",
    "et": "1",
    "ein": "1",
    "to": "2",
    "tre": "3",
    "fire": "4",
    "fem": "5",
    "seks": "6",
    "sju": "7",
    "syv": "7",
    "åtte": "8",
    "ni": "9",
}

NORWEGIAN_CONFIG = LanguageConfig(
    code="no",
    roman_numerals_uppercase_only=True,
    expand_all_caps_letter_by_letter=False,
    decimal_separator=",",
    decimal_word="komma",
    thousand_separator=" ",
    symbols_to_words={
        "@": "krollalfa",
        ".": "punkt",
        "+": "plus",
        "=": "er lik med",
        ">": "storre enn",
        "<": "mindre enn",
        "°": "grader",
        "°C": "grader celsius",
        "°F": "grader fahrenheit",
        "%": "prosent",
    },
    currency_symbol_to_word={
        "€": "euros",
        "$": "dollars",
        "£": "pounds",
        "¢": "cent",
        "¥": "yens",
        "kr": "kroner",
    },
    filler_words=[
        "eh",
        "øh",
        "hm",
        "hmm",
        "mm",
        "mhm",
        "altså",
        "liksom",
        "bare",
        "nå",
        "a",
        "aa",
        "mmm",
    ],
    digit_words=_NORWEGIAN_DIGIT_WORDS,
    number_words=[
        *_NORWEGIAN_DIGIT_WORDS,
        "ti",
        "elleve",
        "tolv",
        "tretten",
        "fjorten",
        "femten",
        "seksten",
        "sytten",
        "atten",
        "nitten",
        "tjue",
        "tyve",
        "tretti",
        "førti",
        "forti",
        "femti",
        "seksti",
        "sytti",
        "åtti",
        "atti",
        "nitti",
        "hundre",
        "tusen",
        "million",
        "millioner",
        "milliard",
        "milliarder",
        "billion",
        "billioner",
    ],
    plus_word="plus",
)


@register_language
class NorwegianOperators(LanguageOperators):
    def __init__(self) -> None:
        super().__init__(NORWEGIAN_CONFIG)
        self._number_normalizer = NorwegianNumberNormalizer(
            NORWEGIAN_CONFIG.currency_symbol_to_word,
        )

    def expand_written_numbers(self, text: str) -> str:
        """Convert Norwegian spelled-out numbers to digits (e.g. tjue fem → 25)."""
        return self._number_normalizer(text)

    def get_word_replacements(self) -> dict[str, str]:
        from normalization.languages.norwegian.replacements import (
            NORWEGIAN_REPLACEMENTS,
        )

        return NORWEGIAN_REPLACEMENTS
