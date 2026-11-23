import re
import sys
import unicodedata

from normalization.languages.arabic.number_normalizer import ArabicNumberNormalizer
from normalization.languages.arabic.replacements import ARABIC_REPLACEMENTS
from normalization.languages.base import LanguageConfig, LanguageOperators
from normalization.languages.registry import register_language

# Short vowels, tanween, shadda, sukun and related marks (U+064B–U+065F) plus
# the superscript alef. Transcripts rarely agree on vocalization, and
# remove_symbols would otherwise turn each mark into a word-splitting space.
_HARAKAT: dict[str, str] = {chr(c): "" for c in range(0x064B, 0x0660)} | {"\u0670": ""}

# Tatweel / kashida: purely typographic letter elongation (عـــربي → عربي).
_TATWEEL: dict[str, str] = {"\u0640": ""}

# Orthographic variants that transcribers and STT engines use interchangeably.
# Folding them is standard practice for Arabic WER scoring.
_LETTER_VARIANTS: dict[str, str] = {
    "أ": "ا",  # alef with hamza above
    "إ": "ا",  # alef with hamza below
    "آ": "ا",  # alef with madda
    "ٱ": "ا",  # alef wasla
    "ى": "ي",  # alef maqsura
    "ة": "ه",  # ta marbuta
    "ی": "ي",  # Persian yeh
    "ک": "ك",  # keheh
}

# Hamza seats, folded by normalize_spelling_variants rather than character by
# character: the seat before و varies by country and must be read with the next
# letter first (see _RE_HAMZA_BEFORE_WAW).
_HAMZA_SEATS: dict[str, str] = {
    "ؤ": "و",  # waw with hamza above
    "ئ": "ي",  # yeh with hamza above
}

# A hamza before و inside a word is written on a waw (مسؤول, رؤوس), on a yeh
# (مسئول, the usual Egyptian spelling) or on the line (رءوس, يقرءون): grammars
# give these as alternatives when a long ū follows the hamza. All three are
# written as و so that ؤ → و then folds them to one word. A ئ before another
# letter (بيئة, هيئة) and a word-final ء (سماء) are not matched.
_RE_HAMZA_BEFORE_WAW = re.compile(r"(?<=\w)[ئءؤ](?=و)")

# Upper bound of the code points scanned for format characters: the last
# Unicode plane that holds any (tags, U+E0001-U+E007F, are in plane 14).
_LAST_FORMAT_CODE_POINT = 0xE007F

# Every format character (General_Category Cf): direction marks (LRM, RLM,
# ALM U+061C, the embeddings and isolates), ZWSP, ZWNJ, ZWJ, word joiner, BOM,
# the end-of-ayah sign. They steer display, never spell a letter, and an
# editor inserts them silently around mixed Arabic and Latin text.
_FORMAT_CHARACTERS: dict[str, str] = {
    chr(c): ""
    for c in range(min(sys.maxunicode, _LAST_FORMAT_CODE_POINT) + 1)
    if unicodedata.category(chr(c)) == "Cf"
}

# Arabic-Indic (U+0660–U+0669) and Eastern Arabic-Indic (U+06F0–U+06F9) digits
# become ASCII so every numeric step sees them; the Arabic decimal/thousands
# separators and percent sign map to the characters those steps expect.
_DIGITS_AND_SEPARATORS: dict[str, str] = (
    {chr(0x0660 + d): str(d) for d in range(10)}
    | {chr(0x06F0 + d): str(d) for d in range(10)}
    | {
        "٫": ".",  # Arabic decimal separator
        "٬": ",",  # Arabic thousands separator
        "٪": "%",  # Arabic percent sign
    }
)

# Digit words for digit-by-digit readings (phone numbers, codes). Only the full
# forms: short forms like ست / سبع are also common nouns.
_ARABIC_DIGIT_WORDS: dict[str, str] = {
    "صفر": "0",
    "واحد": "1",
    "اثنين": "2",
    "اثنان": "2",
    "اتنين": "2",
    "ثلاثه": "3",
    "تلاته": "3",
    "اربعه": "4",
    "خمسه": "5",
    "سته": "6",
    "سبعه": "7",
    "ثمانيه": "8",
    "تمانيه": "8",
    "تسعه": "9",
}

# Words inserted by steps (symbols, currencies, fillers) are written in the
# normalized surface form (no hamza seats, alef maqsura or ta marbuta) so they
# match the rest of the normalized text.
ARABIC_CONFIG = LanguageConfig(
    code="ar",
    decimal_separator=".",
    decimal_word="فاصله",
    thousand_separator=",",
    symbols_to_words={
        "@": "ات",
        ".": "نقطه",
        "+": "زايد",
        "=": "يساوي",
        ">": "اكبر من",
        "<": "اصغر من",
        "°": "درجه",
        "°C": "درجه ميويه",
        "°F": "درجه فهرنهايت",
        "%": "بالميه",
    },
    currency_symbol_to_word={
        "$": "دولار",
        "€": "يورو",
        "£": "جنيه",
        "¥": "ين",
    },
    character_replacements={
        **_FORMAT_CHARACTERS,
        **_HARAKAT,
        **_TATWEEL,
        **_LETTER_VARIANTS,
        **_DIGITS_AND_SEPARATORS,
    },
    # "اه" (dialectal "yes") and "امم" ("nations" once alef is folded) are real
    # words, so only the elongated hesitation forms are treated as fillers.
    filler_words=[
        "اهه",
        "اممم",
        "ممم",
    ],
    digit_words=_ARABIC_DIGIT_WORDS,
    # Same vocabulary as digit_words: used by
    # normalize_punctuation_between_number_words so "صفر، خمسة" becomes
    # "صفر خمسة" before convert_digit_word_sequences_to_digits.
    number_words=list(_ARABIC_DIGIT_WORDS),
)

# Every single-letter fold the text has been through when the number normalizer
# reads it: character_replacements, then the hamza seats of
# normalize_spelling_variants. Number tables are folded with it.
ARABIC_SPELLING_FOLDS: dict[str, str] = {
    **(ARABIC_CONFIG.character_replacements or {}),
    **_HAMZA_SEATS,
}


@register_language
class ArabicOperators(LanguageOperators):
    def __init__(self) -> None:
        super().__init__(ARABIC_CONFIG)
        self._number_normalizer = ArabicNumberNormalizer(ARABIC_SPELLING_FOLDS)
        self._hamza_seats = str.maketrans(_HAMZA_SEATS)

    def normalize_spelling_variants(self, text: str) -> str:
        """Write every hamza seat before و as و, then fold ؤ → و and ئ → ي.

        مسؤول / مسئول, شؤون / شئون, رؤوس / رءوس and يقرؤون / يقرءون become one word each.
        """
        text = _RE_HAMZA_BEFORE_WAW.sub("و", text)
        return text.translate(self._hamza_seats)

    def expand_written_numbers(self, text: str) -> str:
        """Convert Arabic spelled-out numbers to digits (e.g. خمسة وعشرون → 25)."""
        return self._number_normalizer(text)

    def get_word_replacements(self) -> dict[str, str]:
        return ARABIC_REPLACEMENTS
