from normalization.languages.base import LanguageConfig, LanguageOperators
from normalization.languages.registry import register_language
from normalization.languages.swedish.number_normalizer import SwedishNumberNormalizer

_SWEDISH_DIGIT_WORDS: dict[str, str] = {
    "noll": "0",
    "ett": "1",
    "en": "1",
    "två": "2",
    "tre": "3",
    "fyra": "4",
    "fem": "5",
    "sex": "6",
    "sju": "7",
    "åtta": "8",
    "nio": "9",
}

SWEDISH_CONFIG = LanguageConfig(
    code="sv",
    decimal_separator=",",
    decimal_word="komma",
    thousand_separator=" ",
    symbols_to_words={
        "@": "snabel a",
        ".": "punkt",
        "+": "plus",
        "=": "är lika med",
        ">": "större än",
        "<": "mindre än",
        "°": "grader",
        "°C": "grader celsius",
        "°F": "grader fahrenheit",
        "%": "procent",
    },
    currency_symbol_to_word={
        "€": "euros",
        "$": "dollars",
        "£": "pounds",
        "¢": "cent",
        "¥": "yens",
        "kr": "kronor",
    },
    filler_words=[
        "eh",
        "äh",
        "öh",
        "hm",
        "hmm",
        "mm",
        "mhm",
        "asså",
        "alltså",
        "liksom",
        "typ",
        "ba",
        "va",
        "nå",
    ],
    digit_words=_SWEDISH_DIGIT_WORDS,
    number_words=[
        *_SWEDISH_DIGIT_WORDS,
        "tio",
        "elva",
        "tolv",
        "tretton",
        "fjorton",
        "femton",
        "sexton",
        "sjutton",
        "arton",
        "aderton",
        "nitton",
        "tjugo",
        "trettio",
        "fyrtio",
        "femtio",
        "sextio",
        "sjuttio",
        "åttio",
        "attio",
        "nittio",
        "hundra",
        "tusen",
        "miljon",
        "miljoner",
        "miljard",
        "miljarder",
        "biljon",
        "biljoner",
    ],
    plus_word="plus",
)


@register_language
class SwedishOperators(LanguageOperators):
    def __init__(self) -> None:
        super().__init__(SWEDISH_CONFIG)
        self._number_normalizer = SwedishNumberNormalizer(
            SWEDISH_CONFIG.currency_symbol_to_word,
        )

    def expand_written_numbers(self, text: str) -> str:
        """Convert Swedish spelled-out numbers to digits (e.g. tjugo fem → 25)."""
        return self._number_normalizer(text)

    def get_word_replacements(self) -> dict[str, str]:
        from normalization.languages.swedish.replacements import SWEDISH_REPLACEMENTS

        return SWEDISH_REPLACEMENTS
