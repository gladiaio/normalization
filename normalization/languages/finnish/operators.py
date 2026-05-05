from normalization.languages.base import LanguageConfig, LanguageOperators
from normalization.languages.finnish.number_normalizer import FinnishNumberNormalizer
from normalization.languages.registry import register_language

_FINNISH_DIGIT_WORDS: dict[str, str] = {
    "nolla": "0",
    "yksi": "1",
    "kaksi": "2",
    "kolme": "3",
    "neljä": "4",
    "viisi": "5",
    "kuusi": "6",
    "seitsemän": "7",
    "kahdeksan": "8",
    "yhdeksän": "9",
}

FINNISH_CONFIG = LanguageConfig(
    code="fi",
    decimal_separator=",",
    decimal_word="pilkku",
    thousand_separator=" ",
    symbols_to_words={
        "@": "at merkki",
        ".": "piste",
        "+": "plus",
        "=": "yhtä kuin",
        ">": "suurempi kuin",
        "<": "pienempi kuin",
        "°": "astetta",
        "°C": "astetta celsius",
        "°F": "astetta fahrenheit",
        "%": "prosenttia",
    },
    currency_symbol_to_word={
        "€": "euros",
        "$": "dollars",
        "£": "pounds",
        "¢": "cent",
        "¥": "yens",
    },
    filler_words=[
        "eh",
        "öö",
        "hm",
        "hmm",
        "mm",
        "mhm",
        "tota",
        "tuota",
        "niinkun",
        "tavallaan",
        "aha",
        "aa",
    ],
    digit_words=_FINNISH_DIGIT_WORDS,
    number_words=[
        *_FINNISH_DIGIT_WORDS,
        "kymmenen",
        "yksitoista",
        "kaksitoista",
        "kolmetoista",
        "neljätoista",
        "viisitoista",
        "kuusitoista",
        "seitsemäntoista",
        "kahdeksantoista",
        "yhdeksäntoista",
        "kymmentä",
        "sata",
        "sataa",
        "tuhat",
        "tuhatta",
        "miljoona",
        "miljoonaa",
        "miljoonan",
        "miljardi",
        "miljardia",
        "miljardin",
        "biljoona",
        "biljoonaa",
        "biljoonan",
    ],
    plus_word="plus",
)


@register_language
class FinnishOperators(LanguageOperators):
    def __init__(self) -> None:
        super().__init__(FINNISH_CONFIG)
        self._number_normalizer = FinnishNumberNormalizer(
            FINNISH_CONFIG.currency_symbol_to_word,
        )

    def expand_written_numbers(self, text: str) -> str:
        """Convert Finnish spelled-out numbers to digits (e.g. kaksi kymmentä viisi → 25)."""
        return self._number_normalizer(text)

    def get_word_replacements(self) -> dict[str, str]:
        from normalization.languages.finnish.replacements import FINNISH_REPLACEMENTS

        return FINNISH_REPLACEMENTS
