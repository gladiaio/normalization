import re

from normalization.languages.base import (
    LanguageConfig,
    LanguageOperators,
)
from normalization.languages.french.number_normalizer import FrenchNumberNormalizer
from normalization.languages.french.replacements import FRENCH_REPLACEMENTS
from normalization.languages.registery import register_language

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

# Sentence-level replacements (multi-word → normalized form).
_FRENCH_SENTENCE_REPLACEMENTS: dict[str, str] = {
    "pour 100": " pourcent ",
    "super predateur": "superprédateur",
    # Number & symbol formatting
    "10 pourcent": "10 pour 100",
    "2 x 0": "00",
    # Grammar & pronoun correction (ASR slur → intended form)
    "le expliquer": "lui expliquer",
    "le avez": "l'avez",
    "on te en a": "on en a",
    "ce est": "c'est",
    "je ai": "j'ai",
    "pdg": "directeur général",
    "ceo": "directeur général",
    "cto": "directeur technique",
    "coo": "directeur opérationnel",
    # sports
    "volley-ball": "volleyball",
    "basket-ball": "basketball",
    "water-polo": "waterpolo",
    # others
    "blogue": "blog",
    "déjà": "déjà vu",
    "e-mail": "email",
    "week-end": "weekend",
    "week-ends": "weekends",
    "porte-monnaie": "portemonnaie",
    "porte-feuille": "portefeuille",
    "porte-documents": "portedocuments",
    "extra-terrestre": "extraterrestre",
    "tire-bouchon": "tirebouchon",
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
    sentence_replacements=_FRENCH_SENTENCE_REPLACEMENTS,
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
        """Expand French elisions (j'ai → je ai, c'est → ce est, d'accord → de accord, etc.)."""
        # j' → je (j'ai, j'avais, j'étais...)
        text = re.sub(r"\bj'", "je ", text, flags=re.IGNORECASE)
        # c' → ce (c'est, c'était...)
        text = re.sub(r"\bc'", "ce ", text, flags=re.IGNORECASE)
        # d' → de (d'accord, d'abord, d'habitude...)
        text = re.sub(r"\bd'", "de ", text, flags=re.IGNORECASE)
        # qu' → que
        text = re.sub(r"\bqu'", "que ", text, flags=re.IGNORECASE)
        # n' → ne (n'est, n'a...)
        text = re.sub(r"\bn'", "ne ", text, flags=re.IGNORECASE)
        # s' → se (s'il, s'est...)
        text = re.sub(r"\bs'", "se ", text, flags=re.IGNORECASE)
        # m' → me, t' → te
        text = re.sub(r"\bm'", "me ", text, flags=re.IGNORECASE)
        text = re.sub(r"\bt'", "te ", text, flags=re.IGNORECASE)
        # l' → le (simplified; l'heure → le heure for normalization consistency)
        text = re.sub(r"\bl'", "le ", text, flags=re.IGNORECASE)
        return text

    def expand_written_numbers(self, text: str) -> str:
        """Convert French spelled-out numbers to digits (vingt trois → 23).

        Uses FrenchNumberNormalizer, which normalizes mixed forms (3 milliards → trois milliards)
        then text2num.alpha2digit.
        """
        return self._number_normalizer(text)

    def get_word_replacements(self) -> dict[str, str]:
        return FRENCH_REPLACEMENTS
