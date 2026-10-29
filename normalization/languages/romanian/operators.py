from normalization.languages.base import LanguageConfig, LanguageOperators
from normalization.languages.registry import register_language
from normalization.languages.romanian.number_normalizer import (
    NUMBER_WORDS,
    RomanianNumberNormalizer,
)
from normalization.languages.romanian.time_normalizer import RomanianTimeNormalizer

_ROMANIAN_DIGIT_WORDS: dict[str, str] = {
    "zero": "0",
    "unu": "1",
    "doi": "2",
    "două": "2",
    "trei": "3",
    "patru": "4",
    "cinci": "5",
    "șase": "6",
    "sase": "6",
    "șapte": "7",
    "sapte": "7",
    "opt": "8",
    "nouă": "9",
    # Excluded on purpose: "una" (also the pronoun "one"), and the diacritic-less "doua" and
    # "noua", which also spell "a doua" (the second) and "noua" (the new one).
}

ROMANIAN_CONFIG = LanguageConfig(
    code="ro",
    decimal_separator=",",
    # Folded form: the steps that write and match the decimal word run after
    # remove_diacritics, so "3,5" and "trei virgulă cinci" both become "3 virgula 5".
    decimal_word="virgula",
    thousand_separator=".",
    symbols_to_words={
        "@": "arond",
        ".": "punct",
        "+": "plus",
        "=": "egal",
        ">": "mai mare decât",
        "<": "mai mic decât",
        "°": "grade",
        "°C": "grade celsius",
        "°F": "grade fahrenheit",
        "%": "la sută",
    },
    currency_symbol_to_word={
        "€": "euro",
        "$": "dolari",
        "£": "lire",
    },
    filler_words=[
        # Post-diacritics forms: remove_diacritics runs before remove_filler_words, so the
        # hesitations "ăă"/"ăăă" arrive as "aa"/"aaa". A single "ă" is not listed (it becomes
        # "a", a real word), and neither is "îî" (it becomes "ii", the pronoun "îi").
        "aa",
        "aaa",
        "aaaa",
        "ee",
        "eee",
        "mm",
        "mmm",
        "hm",
        "hmm",
        "mhm",
        "ahm",
        "ehm",
        "eh",
    ],
    digit_words=_ROMANIAN_DIGIT_WORDS,
    number_words=NUMBER_WORDS,
    plus_word="plus",
    # Currency codes and acronyms are read as words ("RON", "ANAF"), and "RON" is not "lei".
    expand_all_caps_letter_by_letter=False,
    # Roman numerals only in capitals ("Capitolul VII"): "vii" (you come), "vi" ("vi se
    # pare") and "ii" written without diacritics are everyday words.
    roman_numerals_uppercase_only=True,
)


@register_language
class RomanianOperators(LanguageOperators):
    def __init__(self) -> None:
        super().__init__(ROMANIAN_CONFIG)
        self._time_normalizer = RomanianTimeNormalizer()
        self._number_normalizer = RomanianNumberNormalizer(
            ROMANIAN_CONFIG.currency_symbol_to_word,
            ROMANIAN_CONFIG.decimal_word or "virgula",
        )

    def normalize_numeric_time_formats(self, text: str) -> str:
        """Spoken and dotted clock times to H:MM (e.g. la opt și un sfert → la 8:15).

        Romanian says times with words ("opt și jumătate", "opt fără un sfert"); they are
        converted here, before the time-colon protection, so they end up exactly like a
        written "8:30".
        """
        return self._time_normalizer(text)

    def expand_written_numbers(self, text: str) -> str:
        """Convert Romanian spelled-out numbers to digits (e.g. douăzeci și cinci → 25)."""
        return self._number_normalizer(text)

    def get_word_replacements(self) -> dict[str, str]:
        from normalization.languages.romanian.replacements import ROMANIAN_REPLACEMENTS

        return ROMANIAN_REPLACEMENTS
