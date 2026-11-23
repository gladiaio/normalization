"""Hebrew number normalizer (STT-oriented).

``words2num2`` reads Hebrew only in part: it leaves the masculine forms alone
(``חמישה``, ``שלושה``) and misreads some compounds (``אלפיים ועשרים וחמש``), so
this module parses spelled-out cardinals itself, from the forms of Modern Hebrew
grammar (plene spelling):

- units have a feminine form (``שלוש``, ``חמש``), used for counting and before
  ``מאות``, and a masculine form ending in ``ה`` (``שלושה``, ``חמישה``), used
  before ``מיליון`` and with masculine nouns; both are read;
- teens are a unit followed by ``עשרה`` (feminine) or ``עשר`` (masculine):
  ``חמש עשרה`` = ``חמישה עשר`` = 15, ``שתים עשרה`` = ``שנים עשר`` = 12;
- the order is from the highest element to the lowest, and the conjunction
  ``ו`` is glued to an element, normally the last one: ``מאה עשרים וחמש`` = 125,
  ``חמשת אלפים שש מאות חמישים ושלוש`` = 5653;
- the masculine construct forms (``שלושת`` ... ``עשרת``) are read only before
  ``אלפים`` / ``אלפי``, and ``שני`` / ``שתי`` only before ``מיליון`` /
  ``מיליארד``: anywhere else they quantify a definite noun (``שלושת הילדים``)
  or are another word (``יום שני``, Monday).

Standalone ``אחד`` / ``אחת`` stay words, like English "one", because they double
as pronouns and determiners. ``שנים`` (also "years") and ``שתים`` are read only
before ``עשר`` / ``עשרה``.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_CONJUNCTION = "ו"

# The conjunction glued to digits is written with a hyphen (ו-20): the same text
# remove_symbols later makes of a reference that writes it this way.
_CONJUNCTION_BEFORE_DIGITS = _CONJUNCTION + "-"

_ZERO = "אפס"

# Words for 1: converted only inside a larger number.
_ONES: dict[str, int] = {"אחד": 1, "אחת": 1}

_UNITS: dict[str, int] = {
    # feminine
    "שתיים": 2,
    "שלוש": 3,
    "ארבע": 4,
    "חמש": 5,
    "שש": 6,
    "שבע": 7,
    "שמונה": 8,
    "תשע": 9,
    # masculine
    "שניים": 2,
    "שלושה": 3,
    "ארבעה": 4,
    "חמישה": 5,
    "שישה": 6,
    "שבעה": 7,
    "תשעה": 9,
}

# First word of a teen only (שתים עשרה, שנים עשר); "שנים" alone means "years".
_TEEN_ONLY_UNITS: dict[str, int] = {"שתים": 2, "שנים": 2}

_TEN: dict[str, int] = {"עשר": 10, "עשרה": 10}

_TENS: dict[str, int] = {
    "עשרים": 20,
    "שלושים": 30,
    "ארבעים": 40,
    "חמישים": 50,
    "שישים": 60,
    "שבעים": 70,
    "שמונים": 80,
    "תשעים": 90,
}

_HUNDREDS: dict[str, int] = {"מאה": 100, "מאתיים": 200}

# Plural of מאה, multiplied by the unit before it (שלוש מאות = 300).
_HUNDREDS_PLURAL = "מאות"

# Masculine construct forms, read only before the plural of אלף.
_CONSTRUCT_BEFORE_THOUSANDS: dict[str, int] = {
    "שלושת": 3,
    "ארבעת": 4,
    "חמשת": 5,
    "ששת": 6,
    "שבעת": 7,
    "שמונת": 8,
    "תשעת": 9,
    "עשרת": 10,
}

# Construct forms of 2, read only before מיליון / מיליארד (שני מיליון).
_TWO_CONSTRUCT: dict[str, int] = {"שני": 2, "שתי": 2}

_THOUSAND = "אלף"
_THOUSANDS_PLURAL = ("אלפים", "אלפי")
_TWO_THOUSAND = "אלפיים"

_MILLION = "מיליון"
_BILLION = "מיליארד"

_SCALES: dict[str, int] = {
    _THOUSAND: 1_000,
    **dict.fromkeys(_THOUSANDS_PLURAL, 1_000),
    _MILLION: 1_000_000,
    _BILLION: 1_000_000_000,
}

# Scale words that are a number on their own (אלף = 1000, מיליון = 1000000).
_BARE_SCALES = (_THOUSAND, _MILLION, _BILLION)

_LEXICON = frozenset(
    {
        _ZERO,
        *_ONES,
        *_UNITS,
        *_TEEN_ONLY_UNITS,
        *_TEN,
        *_TENS,
        *_HUNDREDS,
        _HUNDREDS_PLURAL,
        *_CONSTRUCT_BEFORE_THOUSANDS,
        *_TWO_CONSTRUCT,
        *_SCALES,
        _TWO_THOUSAND,
    }
)

_RE_PUNCT_EDGES = re.compile(r"^(\W*)(.*?)(\W*)$", re.DOTALL)
# Hyphen or maqaf (U+05BE) inside a compound written as one token (שתים-עשרה).
_RE_JOINER = re.compile(r"[-־]")

# Stages of the part of a number below one thousand.
_EMPTY, _HUNDRED_DONE, _TENS_DONE, _UNIT_DONE, _TEEN_DONE = range(5)


@dataclass
class _Token:
    raw: str
    """Original text, emitted unchanged when the token is not part of a number."""
    lead: str = ""
    trail: str = ""
    word: str | None = None
    """Number word with any glued conjunction stripped."""
    conj: bool = False
    """True when the conjunction ו is glued to the word."""


class HebrewNumberNormalizer:
    """Convert Hebrew spelled-out cardinal numbers to digits."""

    def __call__(self, text: str) -> str:
        if not text.strip():
            return text
        toks = self._tokenize(text.split())
        out: list[str] = []
        i = 0
        while i < len(toks):
            parsed = self._parse_number(toks, i)
            if parsed is None:
                out.append(toks[i].raw)
                i += 1
                continue
            end, value = parsed
            first, last = toks[i], toks[end - 1]
            conj = _CONJUNCTION_BEFORE_DIGITS if first.conj else ""
            out.append(f"{first.lead}{conj}{value}{last.trail}")
            i = end
        return " ".join(out)

    @staticmethod
    def _number_word(word: str) -> tuple[str, bool] | None:
        """Return (number word, glued conjunction) when ``word`` is one."""
        if word in _LEXICON:
            return word, False
        if word.startswith(_CONJUNCTION) and word[1:] in _LEXICON:
            return word[1:], True
        return None

    def _tokenize(self, words: list[str]) -> list[_Token]:
        toks: list[_Token] = []
        for raw in words:
            lead, word, trail = self._split(raw)
            parts = _RE_JOINER.split(word)
            if len(parts) > 1 and all(self._number_word(p) for p in parts):
                # A compound joined by a hyphen or maqaf: one token per element.
                for index, part in enumerate(parts):
                    number = self._number_word(part)
                    assert number is not None
                    toks.append(
                        _Token(
                            part,
                            lead if index == 0 else "",
                            trail if index == len(parts) - 1 else "",
                            number[0],
                            number[1],
                        )
                    )
                continue
            number = self._number_word(word)
            if number is None:
                toks.append(_Token(raw))
            else:
                toks.append(_Token(raw, lead, trail, number[0], number[1]))
        return toks

    @staticmethod
    def _split(raw: str) -> tuple[str, str, str]:
        match = _RE_PUNCT_EDGES.match(raw)
        assert match is not None
        return match.group(1), match.group(2), match.group(3)

    def _parse_number(self, toks: list[_Token], start: int) -> tuple[int, int] | None:
        """Parse the longest number starting at ``start``: (end index, value)."""
        if toks[start].word is None:
            return None
        total = 0
        current = 0
        stage = _EMPTY
        scale_floor = _SCALES[_BILLION] * 1_000
        last_unit = 0
        best: tuple[int, int] | None = None
        i = start
        while i < len(toks):
            tok = toks[i]
            word = tok.word
            # A punctuation mark between two words ends the number.
            if word is None or (i > start and (tok.lead or toks[i - 1].trail)):
                break
            next_word = toks[i + 1].word if i + 1 < len(toks) else None
            unit = _ONES.get(word) or _UNITS.get(word) or _TEEN_ONLY_UNITS.get(word)
            if word == _ZERO:
                if i > start:
                    break
                best = (i + 1, 0)
                break
            if unit:
                if word in _TEEN_ONLY_UNITS and next_word not in _TEN:
                    break
                if stage not in (_EMPTY, _HUNDRED_DONE, _TENS_DONE):
                    break
                current += unit
                last_unit = unit
                stage = _UNIT_DONE
            elif word in _TEN:
                if stage == _UNIT_DONE and not tok.conj and current % 100 < 10:
                    current += 10
                elif stage in (_EMPTY, _HUNDRED_DONE):
                    current += 10
                else:
                    break
                stage = _TEEN_DONE
            elif word in _TENS:
                if stage not in (_EMPTY, _HUNDRED_DONE):
                    break
                current += _TENS[word]
                stage = _TENS_DONE
            elif word in _HUNDREDS:
                if stage != _EMPTY:
                    break
                current += _HUNDREDS[word]
                stage = _HUNDRED_DONE
            elif word == _HUNDREDS_PLURAL:
                if stage != _UNIT_DONE or current != last_unit or last_unit < 3:
                    break
                current = last_unit * 100
                stage = _HUNDRED_DONE
            elif word in _CONSTRUCT_BEFORE_THOUSANDS:
                if stage != _EMPTY or current or next_word not in _THOUSANDS_PLURAL:
                    break
                current = _CONSTRUCT_BEFORE_THOUSANDS[word]
                stage = _UNIT_DONE
            elif word in _TWO_CONSTRUCT:
                if stage != _EMPTY or current or next_word not in (_MILLION, _BILLION):
                    break
                current = _TWO_CONSTRUCT[word]
                stage = _UNIT_DONE
            elif word == _TWO_THOUSAND:
                if stage != _EMPTY or current or scale_floor <= 1_000:
                    break
                total += 2_000
                scale_floor = 1_000
            elif word in _SCALES:
                scale = _SCALES[word]
                if scale >= scale_floor:
                    break
                if current:
                    total += current * scale
                elif word in _BARE_SCALES and stage == _EMPTY:
                    total += scale
                else:
                    break
                current = 0
                stage = _EMPTY
                scale_floor = scale
            else:
                break
            i += 1
            best = (i, total + current)
        if best is None:
            return None
        end, value = best
        # A lone "one" stays a word.
        if end == start + 1 and toks[start].word in _ONES:
            return None
        return best
