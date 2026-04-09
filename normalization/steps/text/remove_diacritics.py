import unicodedata

from normalization.languages.base import LanguageOperators
from normalization.steps.base import TextStep
from normalization.steps.registry import register_step

_ADDITIONAL_DIACRITICS = {
    "œ": "oe",
    "Œ": "OE",
    "ø": "o",
    "Ø": "O",
    "æ": "ae",
    "Æ": "AE",
    "ß": "ss",
    "ẞ": "SS",
    "đ": "d",
    "Đ": "D",
    "ð": "d",
    "Ð": "D",
    "þ": "th",
    "Þ": "th",
    "ł": "l",
    "Ł": "L",
}


@register_step
class RemoveDiacriticsStep(TextStep):
    """Normalize text by removing diacritics and converting special accented letters to their ASCII equivalents. (é -> e, ê -> e, etc.)"""

    name = "remove_diacritics"

    def __call__(self, text: str, operators: LanguageOperators) -> str:
        res = ""
        for c in unicodedata.normalize("NFKD", text):
            if c in _ADDITIONAL_DIACRITICS:
                res += _ADDITIONAL_DIACRITICS[c]
            elif unicodedata.category(c) != "Mn":
                res += c
        return res
