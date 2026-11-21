"""Shared ASCII-folding of accented characters.

Single source of truth for the ``remove_diacritics`` transform. It is used by
the pipeline step (``normalization.steps.text.remove_diacritics``) and by
``LanguageOperators`` when the operators are built, to fold configured filler
words to the surface form the text has at match time (``remove_diacritics``
runs before ``remove_filler_words`` in the gladia-3 preset).
"""

import unicodedata

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


def remove_diacritics(text: str) -> str:
    """Remove diacritics and convert special accented letters to their ASCII equivalents (é -> e, ß -> ss, etc.)."""
    res = ""
    for c in unicodedata.normalize("NFKD", text):
        if c in _ADDITIONAL_DIACRITICS:
            res += _ADDITIONAL_DIACRITICS[c]
        elif unicodedata.category(c) != "Mn":
            res += c
    return res
