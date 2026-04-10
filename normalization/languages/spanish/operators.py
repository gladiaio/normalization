import re

from normalization.languages.base import LanguageConfig, LanguageOperators
from normalization.languages.registry import register_language
from normalization.languages.spanish.number_normalizer import SpanishNumberNormalizer
from normalization.languages.spanish.replacements import SPANISH_REPLACEMENTS

_ONE_TO_NINE: dict[str, str] = {
    "uno": "1",
    "dos": "2",
    "tres": "3",
    "cuatro": "4",
    "cinco": "5",
    "seis": "6",
    "siete": "7",
    "ocho": "8",
    "nueve": "9",
}

SPANISH_CONFIG = LanguageConfig(
    code="es",
    decimal_separator=",",
    decimal_word="punto",
    thousand_separator=".",
    symbols_to_words={
        "@": "arroba",
        ".": "punto",
        "+": "más",
        "=": "igual a",
        ">": "mayor que",
        "<": "menor que",
        "°": "grado",
        "°C": "grados celsius",
        "°F": "grados fahrenheit",
        "%": "por ciento",
    },
    currency_symbol_to_word={
        "€": "euros",
        "$": "dólares",
        "£": "libras",
        "¢": "céntimos",
        "¥": "yenes",
    },
    filler_words=[
        "eh",
        "ehm",
        "mm",
        "mh",
        "bueno",
        "pues",
        "o sea",
        "tipo",
        "vale",
        "vaya",
        "mira",
        "hombre",
        "mujer",
        "digo",
        "entonces",
        "claro",
        "vamos",
        "este",
        "esta",
    ],
    sentence_replacements=None,
    digit_words={"cero": "0", **_ONE_TO_NINE},
    number_words=[
        "cero",
        *_ONE_TO_NINE,
        "diez",
        "once",
        "doce",
        "trece",
        "catorce",
        "quince",
        "dieciséis",
        "dieciseis",
        "diecisiete",
        "dieciocho",
        "diecinueve",
        "veinte",
        "veintiuno",
        "veintidos",
        "veintitres",
        "veinticuatro",
        "veinticinco",
        "veintiseis",
        "veintisiete",
        "veintiocho",
        "veintinueve",
        "treinta",
        "cuarenta",
        "cincuenta",
        "sesenta",
        "setenta",
        "ochenta",
        "noventa",
        "cien",
        "ciento",
        "doscientos",
        "trescientos",
        "cuatrocientos",
        "quinientos",
        "seiscientos",
        "setecientos",
        "ochocientos",
        "novecientos",
        "mil",
        "millón",
        "millones",
        "mil millones",
        "billón",
        "billones",
    ],
    plus_word="más",
)


@register_language
class SpanishOperators(LanguageOperators):
    def __init__(self):
        super().__init__(SPANISH_CONFIG)
        self._number_normalizer = SpanishNumberNormalizer()

    def fix_one_word_in_numeric_contexts(self, text: str) -> str:
        text = re.sub(r"(\d+)\s+uno\s+uno\b", r"\1 1 1", text)
        text = re.sub(r"\buno\s+uno\s+(\d)", r"1 1 \1", text)
        text = re.sub(r"(\d+)\s+uno\s+(\d)", r"\1 1 \2", text)
        text = re.sub(r"(\d+)\s+uno\b", r"\1 1", text)
        text = re.sub(r"\b(\d+)uno\b", r"\1 1", text)
        text = re.sub(r"\buno\s+(\d)", r"1 \1", text)
        text = re.sub(r"^uno\s+(?=[a-z])", "1 ", text)
        return text

    def get_word_replacements(self) -> dict[str, str]:
        return SPANISH_REPLACEMENTS

    def expand_written_numbers(self, text: str) -> str:
        return self._number_normalizer(text)
