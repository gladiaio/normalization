import re

from normalization.languages.base import (
    LanguageConfig,
    LanguageOperators,
)
from normalization.languages.french.number_normalizer import FrenchNumberNormalizer
from normalization.languages.french.replacements import FRENCH_REPLACEMENTS
from normalization.languages.french.sentence_replacements import (
    FRENCH_SENTENCE_REPLACEMENTS,
)
from normalization.languages.registry import register_language

# French digit words (0-9) for steps that need digit-word recognition.
_FRENCH_DIGIT_WORDS: dict[str, str] = {
    "zéro": "0",
    "un": "1",
    "deux": "2",
    "trois": "3",
    "quatre": "4",
    "cinq": "5",
    "six": "6",
    "sept": "7",
    "huit": "8",
    "neuf": "9",
}

FRENCH_CONFIG = LanguageConfig(
    code="fr",
    decimal_separator=",",
    decimal_word="virgule",
    thousand_separator=" ",
    symbols_to_words={
        "@": "arobase",
        ".": "point",
        "+": "plus",
        "=": "égal à",
        ">": "plus grand que",
        "<": "plus petit que",
        "°": "degré",
        "°C": "degrés celsius",
        "°F": "degrés fahrenheit",
        "%": "pourcent",
    },
    currency_symbol_to_word={
        "€": "euros",
        "$": "dollars",
        "£": "livres",
        "¢": "cents",
        "¥": "yens",
    },
    filler_words=["euh", "hum", "beh", "bah", "ben", "hein"],
    digit_words=_FRENCH_DIGIT_WORDS,
    sentence_replacements=FRENCH_SENTENCE_REPLACEMENTS,
    number_words=[
        "zéro",
        "un",
        "deux",
        "trois",
        "quatre",
        "cinq",
        "six",
        "sept",
        "huit",
        "neuf",
        "dix",
        "onze",
        "douze",
        "treize",
        "quatorze",
        "quinze",
        "seize",
        "vingt",
        "trente",
        "quarante",
        "cinquante",
        "soixante",
        "septante",
        "octante",
        "huitante",
        "nonante",
        "cent",
        "mille",
        "million",
        "millions",
        "milliard",
        "milliards",
        "billion",
        "billions",
        "trillion",
        "trillions",
    ],
    plus_word="plus",
)


@register_language
class FrenchOperators(LanguageOperators):
    """French language operators: contractions, written numbers, word replacements."""

    def __init__(self) -> None:
        super().__init__(FRENCH_CONFIG)
        self._number_normalizer = FrenchNumberNormalizer()

    def expand_contractions(self, text: str) -> str:
        """Expand French informal spoken contractions before consonants only.

        French elision (apostrophe before a vowel or h) is the standard written form and
        must be preserved: j'ai, c'est, l'ami, d'accord stay as-is because expanding them
        would produce adjacent vowels that are incorrect in written French.

        Only expand when the apostrophe is followed by a consonant — those are informal
        spoken reductions (j'veux → je veux, j'suis → je suis, s'pas → se pas).
        """
        # Vowels + h: elision before these is standard written French — do not expand.
        vowels = "aàâeéèêiîïoôuùûyh"
        _V = rf"(?![{vowels}{vowels.upper()}])"
        text = re.sub(rf"\bj'{_V}", "je ", text, flags=re.IGNORECASE)
        text = re.sub(rf"\bc'{_V}", "ce ", text, flags=re.IGNORECASE)
        text = re.sub(rf"\bd'{_V}", "de ", text, flags=re.IGNORECASE)
        text = re.sub(rf"\bqu'{_V}", "que ", text, flags=re.IGNORECASE)
        text = re.sub(rf"\bn'{_V}", "ne ", text, flags=re.IGNORECASE)
        text = re.sub(rf"\bs'{_V}", "se ", text, flags=re.IGNORECASE)
        text = re.sub(rf"\bm'{_V}", "me ", text, flags=re.IGNORECASE)
        text = re.sub(rf"\bt'{_V}", "te ", text, flags=re.IGNORECASE)
        text = re.sub(rf"\bl'{_V}", "le ", text, flags=re.IGNORECASE)
        return text

    def expand_written_numbers(self, text: str) -> str:
        """Convert French spelled-out numbers to digits (vingt trois → 23).

        Uses FrenchNumberNormalizer, which normalizes mixed forms (3 milliards → trois milliards)
        then text2num.alpha2digit.
        """
        return self._number_normalizer(text)

    def get_word_replacements(self) -> dict[str, str]:
        return FRENCH_REPLACEMENTS
