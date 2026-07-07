from normalization.languages.base import LanguageConfig, LanguageOperators
from normalization.languages.danish.number_normalizer import DanishNumberNormalizer
from normalization.languages.danish.sentence_replacements import (
    DANISH_SENTENCE_REPLACEMENTS,
)
from normalization.languages.registry import register_language

_DANISH_DIGIT_WORDS: dict[str, str] = {
    "nul": "0",
    "en": "1",
    "et": "1",
    "to": "2",
    "tre": "3",
    "fire": "4",
    "fem": "5",
    "seks": "6",
    "syv": "7",
    "otte": "8",
    "ni": "9",
}

DANISH_CONFIG = LanguageConfig(
    code="da",
    decimal_separator=",",
    decimal_word="komma",
    thousand_separator=".",
    symbols_to_words={
        "@": "snabel a",
        ".": "punktum",
        "+": "plus",
        "=": "er lig med",
        ">": "større end",
        "<": "mindre end",
        "°": "grader",
        "°C": "grader celsius",
        "°F": "grader fahrenheit",
        "%": "procent",
    },
    currency_symbol_to_word={
        "€": "euro",
        "$": "dollar",
        "£": "pund",
        "¢": "cent",
        "¥": "yen",
        "kr": "kroner",
    },
    filler_words=[
        # Post-diacritics forms: remove_diacritics runs before remove_filler_words,
        # so ø→o and å→a conversions have already happened at match time.
        # "ohm" (from "øhm") is intentionally excluded: after diacritics removal it
        # collides with the SI unit "ohm", which would be silently deleted in phrases
        # like "modstanden er 10 ohm".
        "oh",  # from "øh"
        "hm",
        "hmm",
        "mm",
        "mhm",
        "altsa",  # from "altså"
        "na",  # from "nå"
    ],
    digit_words=_DANISH_DIGIT_WORDS,
    number_words=[
        *_DANISH_DIGIT_WORDS,
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
        "tyve",
        "tredive",
        "tredve",
        "fyrre",
        "halvtreds",
        "tres",
        "halvfjerds",
        "firs",
        "halvfems",
        "hundrede",
        "tusind",
        "tusinde",
        "million",
        "millioner",
        "milliard",
        "milliarder",
        "billion",
        "billioner",
    ],
    plus_word="plus",
    sentence_replacements=DANISH_SENTENCE_REPLACEMENTS,
)


@register_language
class DanishOperators(LanguageOperators):
    def __init__(self) -> None:
        super().__init__(DANISH_CONFIG)
        self._number_normalizer = DanishNumberNormalizer(
            DANISH_CONFIG.currency_symbol_to_word,
        )

    def expand_written_numbers(self, text: str) -> str:
        """Convert Danish spelled-out numbers to digits (e.g. en og tyve → 21)."""
        return self._number_normalizer(text)

    def get_word_replacements(self) -> dict[str, str]:
        from normalization.languages.danish.replacements import DANISH_REPLACEMENTS

        return DANISH_REPLACEMENTS
