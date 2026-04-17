import re

from normalization.languages.base import (
    LanguageConfig,
    LanguageOperators,
)
from normalization.languages.dutch.number_normalizer import DutchNumberNormalizer
from normalization.languages.dutch.sentence_replacements import (
    DUTCH_SENTENCE_REPLACEMENTS,
)
from normalization.languages.registry import register_language

# Flemish apostrophe clitics (straight or typographic apostrophe). (?<!\w) avoids
# English-style possessives (e.g. Jan's) where the apostrophe follows a letter.
_APOST = r"['\u2019]"
_TEMPORAL_S_AFTER = (
    r"ochtends|morgens|middags|namiddags|avonds|nachts|"
    r"zaterdags|zondags|weekend|weekends"
)
_RE_TEMPORAL_S = re.compile(
    rf"(?<!\w){_APOST}s(\s+)({_TEMPORAL_S_AFTER})\b",
    re.IGNORECASE,
)
_RE_CLITIC_S = re.compile(rf"(?<!\w){_APOST}s\b", re.IGNORECASE)
_RE_CLITIC_TRNKM = re.compile(rf"(?<!\w){_APOST}([trnkm])\b", re.IGNORECASE)

_CLITIC_LETTER_TO_WORD = {
    "t": "het",
    "r": "er",
    "n": "een",
    "k": "ik",
    "m": "hem",
}

DUTCH_CONFIG = LanguageConfig(
    code="nl",
    decimal_separator=",",
    decimal_word="komma",
    thousand_separator=" ",
    symbols_to_words={
        "@": "apenstaartje",
        ".": "punt",
        "+": "plus",
        "=": "gelijk aan",
        ">": "groter dan",
        "<": "kleiner dan",
        "°": "graden",
        "°C": "graden celsius",
        "°F": "graden fahrenheit",
        "%": "procent",
    },
    currency_symbol_to_word={
        "€": "euros",
        "$": "dollars",
        "£": "ponden",
        "¢": "cent",
        "¥": "yens",
    },
    filler_words=[
        "ah",
        "allee",
        "alee",
        "eh",
        "ehm",
        "hé",
        "hè",
        "he",
        "hm",
        "hmm",
        "mm",
        "mmm",
        "mhm",
        "nou",
        "o",
        "oke",
        "okee",
        "oké",
        "uh",
    ],
    sentence_replacements=DUTCH_SENTENCE_REPLACEMENTS,
)


@register_language
class DutchOperators(LanguageOperators):
    def __init__(self):
        super().__init__(DUTCH_CONFIG)
        self._number_normalizer = DutchNumberNormalizer(
            DUTCH_CONFIG.currency_symbol_to_word,
        )

    def expand_written_numbers(self, text: str) -> str:
        return self._number_normalizer(text)

    def expand_contractions(self, text: str) -> str:
        def _temporal_sub(m: re.Match[str]) -> str:
            return f"des{m.group(1)}{m.group(2).lower()}"

        text = _RE_TEMPORAL_S.sub(_temporal_sub, text)
        text = _RE_CLITIC_S.sub("is", text)

        def _clitic_sub(m: re.Match[str]) -> str:
            return _CLITIC_LETTER_TO_WORD[m.group(1).lower()]

        text = _RE_CLITIC_TRNKM.sub(_clitic_sub, text)
        return text

    def get_word_replacements(self) -> dict[str, str]:
        from normalization.languages.dutch.replacements import DUTCH_REPLACEMENTS

        return DUTCH_REPLACEMENTS
