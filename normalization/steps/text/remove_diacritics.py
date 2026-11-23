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

# Scripts whose combining marks are accents or vowel points on a complete letter: dropping them
# folds "é" to "e", "ё" to "е", "שָׁ" to "ש" and "مُ" to "م". In every other script (Devanagari,
# Bengali and the other Indic scripts, kana, Thai...) a combining mark is part of the letter or
# the syllable (a vowel sign, a virama, a voicing mark), and dropping it changes the word.
_FOLDING_SCRIPTS = frozenset({"LATIN", "GREEK", "CYRILLIC", "HEBREW", "ARABIC"})

# A mark kept on a base of a folding script: the breve of Cyrillic "й" (и + U+0306) makes another
# letter, not an accented "и".
_KEPT_MARKS = {"̆": frozenset("иИ")}


def _script(char: str) -> str:
    """The script of a letter, read from its Unicode name ("LATIN SMALL LETTER E" -> "LATIN")."""
    return unicodedata.name(char, "").split(" ", 1)[0]


def _drops(mark: str, base: str | None) -> bool:
    """Whether the nonspacing ``mark`` is a diacritic of ``base``, the character it sits on."""
    if base is None or not base.isalpha():
        return True  # a mark on nothing, a space or a digit is noise
    if base in _KEPT_MARKS.get(mark, ()):
        return False
    return _script(base) in _FOLDING_SCRIPTS


@register_step
class RemoveDiacriticsStep(TextStep):
    """Normalize text by removing diacritics and converting special accented letters to their ASCII equivalents. (é -> e, ê -> e, etc.)

    A nonspacing mark is removed only on a Latin, Greek, Cyrillic, Hebrew or
    Arabic letter (accents, niqqud, harakat). In the other scripts it is part
    of the letter and is kept (Hindi "लूना", Bengali "বাংলা", Japanese "です"),
    and so is the breve of Russian "й". A letter that keeps a mark is
    recomposed (NFC).
    """

    name = "remove_diacritics"

    def __call__(self, text: str, operators: LanguageOperators) -> str:
        parts: list[str] = []
        base: str | None = None  # the last character that is not a combining mark
        start = 0  # where base's cluster starts in parts
        kept = False  # whether base's cluster keeps a mark: recomposed when it ends
        for c in unicodedata.normalize("NFKD", text):
            if unicodedata.category(c)[0] == "M":
                if unicodedata.category(c) == "Mn" and _drops(c, base):
                    continue
                parts.append(c)
                kept = True
                continue
            if kept:
                parts[start:] = [unicodedata.normalize("NFC", "".join(parts[start:]))]
            kept = False
            base = c
            start = len(parts)
            parts.append(_ADDITIONAL_DIACRITICS.get(c, c))
        if kept:
            parts[start:] = [unicodedata.normalize("NFC", "".join(parts[start:]))]
        return "".join(parts)
