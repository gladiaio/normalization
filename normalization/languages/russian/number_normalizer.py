"""Russian number normalizer (STT-oriented).

Spelled-out cardinals are read by ``words2num2`` (``двадцать пять`` -> ``25``,
``пять процентов`` -> ``5 процентов``, ``шесть целых пять десятых`` -> ``6,5``),
with two guards:

- a form of ``один`` with no number word next to it stays a word, like English
  "one": it is also the pronoun and adjective "one, alone, the same"
  (``один из них``, ``он один``);
- the word after ``полтора`` / ``полторы`` / ``полутора`` (one and a half) is
  left alone, so ``полторы тысячи`` does not become ``полторы 1000``.

Then, only right after a number, the forms a reader takes as the same words
are folded to one form. Russian nouns change their ending with the case and
the numeral (``1 километр``, ``2 километра``, ``5 километров``, ``в 5 километрах``),
while an abbreviation has one form, so the spoken forms are folded to the
abbreviation and never the other way:

- units of measurement (ГОСТ 8.417): ``километров`` -> ``км``, ``метра`` -> ``м``,
  ``сантиметров`` -> ``см``, ``килограммов`` -> ``кг``;
- millimetre: ``мм`` and ``миллиметров`` -> ``миллиметров``, a word, because
  the symbol ``мм`` is also a hesitation filler;
- the year: ``году`` / ``года`` / ``год`` after a number -> ``г``, the form of the
  abbreviation ``г.`` once ``remove_symbols`` drops its period;
- ``процент`` / ``процента`` / ``процентов`` -> ``процентов``, the word
  ``symbols_to_words`` gives ``%``;
- ``тыс.`` / ``млн`` / ``млрд`` and the words ``тысяч`` / ``миллионов`` /
  ``миллиардов`` after an integer are multiplied out (``5 млн`` -> ``5000000``),
  as ``words2num2`` does for ``пять миллионов``.

The era abbreviation ``н. э.`` (``до н. э.``) is expanded to ``нашей эры``, a
fixed genitive phrase, when a year, a century or ``до`` comes before it. It
cannot be left as ``н э``: ``э`` is a hesitation filler and would be removed.

One-letter words are never treated as abbreviations unless a number comes
right before them, so the prepositions ``в``, ``к`` and ``с`` are never touched.
"""

from __future__ import annotations

import re

from words2num2 import words2num_sentence

_LANG = "ru"

# Forms of "один" that words2num2 reads as 1 even when they stand alone.
_ONE_FORMS = frozenset(
    {
        "один",
        "одна",
        "одно",
        "одного",
        "одной",
        "одною",
        "одному",
        "одним",
        "одну",
        "одном",
    }
)

# "One and a half": words2num2 reads the scale word after it on its own.
_ONE_AND_A_HALF = frozenset({"полтора", "полторы", "полутора"})

# Scale words that words2num2 reads only after a count ("один миллион").
_RE_SCALE_WORD = re.compile(r"^(?:тысяч|миллион|миллиард)\w*$", re.IGNORECASE)

# Private-use characters that words2num2 leaves alone, to hide a word from it.
_MASK_OPEN = ""
_MASK_CLOSE = ""
_RE_MASKED = re.compile(f"{_MASK_OPEN}(.*?){_MASK_CLOSE}")

_RE_EDGE_PUNCT = re.compile(r"^\W+|\W+$")

# Noun endings of the hard declension (километр, метр, ...): nominative,
# genitive, dative, instrumental and prepositional, singular and plural.
_NOUN_ENDINGS = r"(?:а|у|ом|е|ы|ов|ам|ами|ах)?"

# Spoken unit -> its abbreviation (ГОСТ 8.417; written without a period).
_UNITS: dict[str, str] = {
    "километр": "км",
    "сантиметр": "см",
    "метр": "м",
    "килограмм": "кг",
}

# Forms of "год" after a number. "лет" (the genitive plural that a duration
# takes: "5 лет") is not "г." and stays.
_YEAR_FORMS = r"(?:год|года|году|годом|годе)"
_YEAR_ABBREVIATION = "г"

# Millimetre is the one unit folded to a word: its symbol "мм" is also a
# hesitation filler, which would delete it ("5 мм" -> "5"). After a number, the
# symbol and every case form of "миллиметр" become "миллиметров", a token the
# filler list cannot match. A standalone "мм" stays a filler.
_MILLIMETRE_FORMS = r"мм\.?|миллиметр" + _NOUN_ENDINGS
_MILLIMETRE_WORD = "миллиметров"

_PERCENT_FORMS = r"процент(?:а|у|ом|е|ы|ов|ам|ами|ах)?"
_PERCENT_WORD = "процентов"

# Written scales after an integer and their value. "тыс." before an era is the
# millennium ("3 тыс. до н. э."), not a thousand, and is left alone.
_SCALES: tuple[tuple[str, int], ...] = (
    (
        r"тыс\.?(?!\s*(?:до\s+)?(?:н\.\s?э|нашей\s+эры))"
        r"|тысяч(?:а|и|у|ей|ам|ами|ах)?",
        1_000,
    ),
    (r"млн\.?|миллион" + _NOUN_ENDINGS, 1_000_000),
    (r"млрд\.?|миллиард" + _NOUN_ENDINGS, 1_000_000_000),
)

_ERA_EXPANSION = "нашей эры"
# "н. э." after a year ("79 г.", "79 году", "79"), a century ("I в.", "веке")
# or "до". Without such a word before it, "Н. Э." can be a person's initials.
_RE_ERA = re.compile(
    r"(?P<before>(?:\d|\b(?:до|г|гг|в|вв|год\w*|век\w*))\.?\s+)н\.\s?э\b\.?",
    re.IGNORECASE,
)


def _fold_after_number(pattern: str, replacement: str) -> tuple[re.Pattern, str]:
    return (
        re.compile(rf"(\d)\s+(?:{pattern})\b", re.IGNORECASE),
        rf"\1 {replacement}",
    )


_FOLDS: tuple[tuple[re.Pattern, str], ...] = (
    *(
        _fold_after_number(spoken + _NOUN_ENDINGS, abbreviation)
        for spoken, abbreviation in _UNITS.items()
    ),
    _fold_after_number(_MILLIMETRE_FORMS, _MILLIMETRE_WORD),
    _fold_after_number(_YEAR_FORMS, _YEAR_ABBREVIATION),
    _fold_after_number(_PERCENT_FORMS, _PERCENT_WORD),
)

_RE_SCALES: tuple[tuple[re.Pattern, int], ...] = tuple(
    (re.compile(rf"(?<![\w.,])(\d+)\s+(?:{pattern})(?=\s|$|[^\w.])", re.I), value)
    for pattern, value in _SCALES
)


def _bare(token: str) -> str:
    return _RE_EDGE_PUNCT.sub("", token).lower()


def _is_number_token(token: str) -> bool:
    word = _bare(token)
    if not word:
        return False
    if word.isdigit() or _RE_SCALE_WORD.match(word):
        return True
    return words2num_sentence(word, lang=_LANG) != word


def _mask(token: str) -> str:
    return f"{_MASK_OPEN}{token}{_MASK_CLOSE}"


def _multiply(match: re.Match, value: int) -> str:
    """``5 млн`` -> ``5000000``. When a number word follows (``2 тысячи пятьсот``),
    multiplying would give ``2000 500``, read later as ``2000500``: the scale word
    is kept and hidden from words2num2 instead, so the value never changes."""
    following = match.string[match.end() :].split(" ", 2)
    next_token = following[1] if len(following) > 1 else ""
    if _is_number_token(next_token):
        number, scale = match.group(0).split(maxsplit=1)
        return f"{number} {_mask(scale)}"
    return str(int(match.group(1)) * value)


class RussianNumberNormalizer:
    """Convert Russian spelled-out numbers to digits and fold the words after them."""

    def __call__(self, text: str) -> str:
        if not text.strip():
            return text
        text = _RE_ERA.sub(rf"\g<before>{_ERA_EXPANSION}", text)
        # Before words2num2, which would read "тысячи" in "2 тысячи" on its own.
        for pattern, value in _RE_SCALES:
            text = pattern.sub(lambda m, v=value: _multiply(m, v), text)
        text = self._read_numbers(text)
        for pattern, replacement in _FOLDS:
            text = pattern.sub(replacement, text)
        return text

    def _read_numbers(self, text: str) -> str:
        tokens = text.split(" ")
        masked = list(tokens)
        for i, token in enumerate(tokens):
            word = _bare(token)
            previous = tokens[i - 1] if i > 0 else ""
            following = tokens[i + 1] if i + 1 < len(tokens) else ""
            if word in _ONE_FORMS and not (
                _is_number_token(previous) or _is_number_token(following)
            ):
                masked[i] = _mask(token)
            elif _bare(previous) in _ONE_AND_A_HALF and word:
                masked[i] = _mask(token)
        read = words2num_sentence(" ".join(masked), lang=_LANG)
        return _RE_MASKED.sub(r"\1", read)
