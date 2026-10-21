from normalization.languages.arabic.replacements import ARABIC_REPLACEMENTS
from normalization.languages.base import LanguageConfig, LanguageOperators
from normalization.languages.registry import register_language

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
