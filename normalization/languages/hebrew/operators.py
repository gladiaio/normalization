from normalization.languages.base import LanguageConfig, LanguageOperators
from normalization.languages.hebrew.number_normalizer import HebrewNumberNormalizer
from normalization.languages.hebrew.replacements import HEBREW_REPLACEMENTS
from normalization.languages.registry import register_language

# The geresh (U+05F3) and gershayim (U+05F4) are usually typed as the ASCII
# apostrophe and quotation mark, which word processors turn into the curly
# quotes. Folding the curly quotes back to ASCII lets remove_symbols keep an
# abbreviation or a loan sound whole whichever of them is written
# (צה”ל, צ’יפס -> צהל, ציפס); anywhere else they stay punctuation.
_CURLY_QUOTES_TO_ASCII: dict[str, str] = {
    "’": "'",  # right single quotation mark
    "”": '"',  # right double quotation mark
}

# Final letter forms (ך ם ן ף ץ) are not folded: references and transcripts both
# write them. Plene and defective spellings are not folded either: one more or one
# less ו or י can be another word (לחים / לחם).
HEBREW_CONFIG = LanguageConfig(
    code="he",
    decimal_separator=".",
    thousand_separator=",",
    # How the symbols are read aloud: "@" is commonly called שטרודל, "." נקודה
    # (as in an e-mail or web address), "+" פלוס.
    symbols_to_words={
        "@": "שטרודל",
        ".": "נקודה",
        "+": "פלוס",
    },
    character_replacements=_CURLY_QUOTES_TO_ASCII,
)


@register_language
class HebrewOperators(LanguageOperators):
    def __init__(self) -> None:
        super().__init__(HEBREW_CONFIG)
        self._number_normalizer = HebrewNumberNormalizer()

    def expand_written_numbers(self, text: str) -> str:
        """Convert Hebrew spelled-out numbers to digits (עשרים וחמש -> 25)."""
        return self._number_normalizer(text)

    def get_word_replacements(self) -> dict[str, str]:
        return HEBREW_REPLACEMENTS
