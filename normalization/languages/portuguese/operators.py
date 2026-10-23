import re

from normalization.languages.base import LanguageConfig, LanguageOperators
from normalization.languages.portuguese.clitics import merge_hyphenated_clitics
from normalization.languages.portuguese.number_normalizer import (
    PortugueseNumberNormalizer,
)
from normalization.languages.portuguese.replacements import PORTUGUESE_REPLACEMENTS
from normalization.languages.portuguese.sentence_replacements import (
    PORTUGUESE_SENTENCE_REPLACEMENTS,
)
from normalization.languages.registry import register_language

_PORTUGUESE_DIGIT_WORDS: dict[str, str] = {
    "zero": "0",
    "um": "1",
    "dois": "2",
    "tres": "3",
    "quatro": "4",
    "cinco": "5",
    "seis": "6",
    "sete": "7",
    "oito": "8",
    "nove": "9",
}

PORTUGUESE_CONFIG = LanguageConfig(
    code="pt",
    decimal_separator=",",
    decimal_word="virgula",
    thousand_separator=" ",
    symbols_to_words={
        "@": "arroba",
        ".": "ponto",
        "+": "mais",
        "=": "igual a",
        ">": "maior que",
        "<": "menor que",
        "°": "grau",
        "°C": "graus celsius",
        "°F": "graus fahrenheit",
        "%": "por cento",
    },
    currency_symbol_to_word={
        "€": "euros",
        "$": "dolares",
        "£": "libras",
        "¢": "centavos",
        "¥": "ienes",
    },
    filler_words=[
        # Hesitations / backchannels only — avoid stripping meaningful words
        # (e.g. "claro", "bem" in "tudo bem", "pronto" in "e pronto, foi assim").
        "ah",
        "eh",
        "ehm",
        "entao",
        "portanto",
        "mm",
        "mmm",
        "mhm",
        "hmm",
        "hm",
        "hum",
        "humm",
    ],
    sentence_replacements=PORTUGUESE_SENTENCE_REPLACEMENTS,
    digit_words=_PORTUGUESE_DIGIT_WORDS,
    number_words=[
        *_PORTUGUESE_DIGIT_WORDS,
        "dez",
        "onze",
        "doze",
        "treze",
        "catorze",
        "quinze",
        "dezasseis",
        "dezesseis",
        "dezassete",
        "dezessete",
        "dezoito",
        "dezenove",
        "vinte",
        "trinta",
        "quarenta",
        "cinquenta",
        "sessenta",
        "setenta",
        "oitenta",
        "noventa",
        "cem",
        "cento",
        "mil",
        "milhao",
        "milhoes",
        "milhão",
        "milhões",
        "bilhao",
        "bilhoes",
        "bilhão",
        "bilhões",
    ],
    plus_word="mais",
)


@register_language
class PortugueseOperators(LanguageOperators):
    """Portuguese language operators: clitics, written numbers, word replacements."""

    def __init__(self) -> None:
        super().__init__(PORTUGUESE_CONFIG)
        self._number_normalizer = PortugueseNumberNormalizer(
            PORTUGUESE_CONFIG.digit_words or {}
        )

    def expand_contractions(self, text: str) -> str:
        """Merge hyphenated clitic pronouns (envie-me → enviame)."""
        return merge_hyphenated_clitics(text)

    def expand_written_numbers(self, text: str) -> str:
        """Convert Portuguese spelled-out numbers to digits (vinte e tres → 23)."""
        return self._number_normalizer(text)

    def fix_one_word_in_numeric_contexts(self, text: str) -> str:
        text = re.sub(r"(\d+)\s+um\b", r"\1 1", text, flags=re.IGNORECASE)
        text = re.sub(r"\bum\s+(\d)", r"1 \1", text, flags=re.IGNORECASE)
        text = re.sub(r"(\d+)um\b", r"\1 1", text, flags=re.IGNORECASE)
        text = re.sub(r"\bum(\d)", r"1 \1", text, flags=re.IGNORECASE)
        return text

    def get_word_replacements(self) -> dict[str, str]:
        return PORTUGUESE_REPLACEMENTS
