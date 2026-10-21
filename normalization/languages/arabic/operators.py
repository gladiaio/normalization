from normalization.languages.arabic.replacements import ARABIC_REPLACEMENTS
from normalization.languages.base import LanguageConfig, LanguageOperators
from normalization.languages.registry import register_language

# Short vowels, tanween, shadda, sukun and related marks (U+064B–U+065F) plus
# the superscript alef. Transcripts rarely agree on vocalization, and
# remove_symbols would otherwise turn each mark into a word-splitting space.
_HARAKAT: dict[str, str] = {chr(c): "" for c in range(0x064B, 0x0660)} | {"\u0670": ""}

# Tatweel / kashida: purely typographic letter elongation (عـــربي → عربي).
_TATWEEL: dict[str, str] = {"\u0640": ""}

# Words inserted by steps (symbols, currencies, fillers) are written in the
# normalized surface form so they match the rest of the normalized text.
ARABIC_CONFIG = LanguageConfig(
    code="ar",
    decimal_separator=".",
    decimal_word="فاصله",
    thousand_separator=",",
    symbols_to_words={
        "@": "ات",
        ".": "نقطه",
        "+": "زائد",
        "=": "يساوي",
        ">": "اكبر من",
        "<": "اصغر من",
        "°": "درجه",
        "°C": "درجه مئويه",
        "°F": "درجه فهرنهايت",
        "%": "بالمئه",
    },
    currency_symbol_to_word={
        "$": "دولار",
        "€": "يورو",
        "£": "جنيه",
        "¥": "ين",
    },
    character_replacements={**_HARAKAT, **_TATWEEL},
    filler_words=[
        "اه",
        "اهه",
        "امم",
        "اممم",
        "ممم",
    ],
)


@register_language
class ArabicOperators(LanguageOperators):
    def __init__(self) -> None:
        super().__init__(ARABIC_CONFIG)

    def get_word_replacements(self) -> dict[str, str]:
        return ARABIC_REPLACEMENTS
