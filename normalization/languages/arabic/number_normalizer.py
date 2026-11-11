"""Arabic number normalizer (STT-oriented).

``text2num.alpha2digit`` does not support Arabic, so this module parses spelled-out
cardinals for common transcript patterns: Modern Standard Arabic with its gender and
case variants (``ثلاث``/``ثلاثة``, ``عشرون``/``عشرين``), plus frequent Egyptian and
Levantine spellings (``تلاتة``, ``اتناشر``, ``تلتمية``).

Arabic puts units before tens and chains every further component with the
conjunction ``و`` glued to the next word: ``مئة وخمسة وعشرون`` = 125,
``ألفين وخمسة وعشرين`` = 2025. ``و`` only joins a unit to a tens word, a hundreds
word to its remainder, or a larger scale group to a smaller one; anywhere else it is
the plain "and" and is left alone (``ثلاثة وأربعة`` → ``3 و4``).

Lookups go through the language's ``character_replacements`` so tables can be
written in their usual spelling and still match folded text (``مئة`` and ``مية``
both fold to ``ميه``). Standalone ``واحد``/``أحد`` stay words, like English "one",
because they double as pronouns.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_ZERO = "صفر"

# Words for 1: converted only inside a larger number.
_ONES: dict[str, int] = {"واحد": 1, "واحدة": 1, "أحد": 1, "إحدى": 1}

_UNITS: dict[str, int] = {
    "اثنان": 2,
    "اثنين": 2,
    "اثنتان": 2,
    "اثنتين": 2,
    "اتنين": 2,
    "ثنين": 2,
    "ثنتين": 2,
    "ثلاثة": 3,
    "ثلاث": 3,
    "تلاتة": 3,
    "تلات": 3,
    "أربعة": 4,
    "أربع": 4,
    "خمسة": 5,
    "خمس": 5,
    "ستة": 6,
    "ست": 6,
    "سبعة": 7,
    "سبع": 7,
    "ثمانية": 8,
    "ثماني": 8,
    "ثمان": 8,
    "تمانية": 8,
    "تمنية": 8,
    "تسعة": 9,
    "تسع": 9,
}

# First word of a two-word teen (أحد عشر, اثنا عشر, ثلاثة عشر, ...).
_TEEN_FIRST: dict[str, int] = {
    "أحد": 1,
    "إحدى": 1,
    "اثنا": 2,
    "اثني": 2,
    "اثنتا": 2,
    "اثنتي": 2,
    **_UNITS,
}

_TEN: dict[str, int] = {"عشرة": 10, "عشر": 10}

# Glued dialect teens (Egyptian / Levantine).
_DIALECT_TEENS: dict[str, int] = {
    "حداشر": 11,
    "احداشر": 11,
    "اتناشر": 12,
    "اطناشر": 12,
    "تلتاشر": 13,
    "تلاتاشر": 13,
    "اربعتاشر": 14,
    "اربعطاشر": 14,
    "خمستاشر": 15,
    "خمسطاشر": 15,
    "ستاشر": 16,
    "سطاشر": 16,
    "سبعتاشر": 17,
    "سبعطاشر": 17,
    "تمنتاشر": 18,
    "تمانتاشر": 18,
    "تمنطاشر": 18,
    "تسعتاشر": 19,
    "تسعطاشر": 19,
}

_TENS: dict[str, int] = {
    "عشرون": 20,
    "عشرين": 20,
    "ثلاثون": 30,
    "ثلاثين": 30,
    "تلاتين": 30,
    "أربعون": 40,
    "أربعين": 40,
    "خمسون": 50,
    "خمسين": 50,
    "ستون": 60,
    "ستين": 60,
    "سبعون": 70,
    "سبعين": 70,
    "ثمانون": 80,
    "ثمانين": 80,
    "تمانين": 80,
    "تسعون": 90,
    "تسعين": 90,
}

_HUNDRED_WORDS = ("مئة", "مائة", "مية")

# Unit stems glued to a hundred word (ثلاثمئة, تلتمية, ...).
_HUNDRED_PREFIXES: dict[str, int] = {
    "ثلاث": 3,
    "تلت": 3,
    "تلات": 3,
    "أربع": 4,
    "ربع": 4,
    "خمس": 5,
    "ست": 6,
    "سبع": 7,
    "ثمان": 8,
    "ثماني": 8,
    "تمن": 8,
    "تمان": 8,
    "تسع": 9,
}

_HUNDREDS: dict[str, int] = {
    **dict.fromkeys(_HUNDRED_WORDS, 100),
    "مئتان": 200,
    "مئتين": 200,
    "مائتان": 200,
    "مائتين": 200,
    **{
        prefix + word: value * 100
        for prefix, value in _HUNDRED_PREFIXES.items()
        for word in _HUNDRED_WORDS
    },
}

# Scale words that follow a count (ثلاثة آلاف, خمسة ملايين).
_MULTIPLIERS: dict[str, int] = {
    "ألف": 1_000,
    "ألفا": 1_000,
    "آلاف": 1_000,
    "تلاف": 1_000,
    "مليون": 1_000_000,
    "مليونا": 1_000_000,
    "ملايين": 1_000_000,
    "مليار": 1_000_000_000,
    "مليارا": 1_000_000_000,
    "مليارات": 1_000_000_000,
    "بليون": 1_000_000_000,
}

# Scale words that carry their own count (ألف = 1000, ألفين = 2000), with their scale.
_STANDALONE_SCALES: dict[str, tuple[int, int]] = {
    "ألف": (1_000, 1_000),
    "ألفا": (1_000, 1_000),
    "ألفان": (2_000, 1_000),
    "ألفين": (2_000, 1_000),
    "مليون": (1_000_000, 1_000_000),
    "مليونان": (2_000_000, 1_000_000),
    "مليونين": (2_000_000, 1_000_000),
    "مليار": (1_000_000_000, 1_000_000_000),
    "ملياران": (2_000_000_000, 1_000_000_000),
    "مليارين": (2_000_000_000, 1_000_000_000),
    "بليون": (1_000_000_000, 1_000_000_000),
}

_CONJUNCTION = "و"

_RE_PUNCT_EDGES = re.compile(r"^(\W*)(.*?)(\W*)$", re.DOTALL)


@dataclass
class _Token:
    raw: str
    """Original text, emitted unchanged when the token is not part of a number."""
    lead: str = ""
    trail: str = ""
    word: str | None = None
    """Folded number word (or ASCII digits) with any conjunction stripped."""
    conj: str = ""
    """``"و"`` when glued to the word, ``"و "`` when written as its own token."""


class ArabicNumberNormalizer:
    """Convert Arabic spelled-out numbers to digits."""

    def __init__(self, character_replacements: dict[str, str] | None = None) -> None:
        self._table = str.maketrans(character_replacements or {})
        fold = self._fold
        self._ones = {fold(k): v for k, v in _ONES.items()}
        self._units = {fold(k): v for k, v in _UNITS.items()}
        self._teen_first = {fold(k): v for k, v in _TEEN_FIRST.items()}
        self._ten = {fold(k): v for k, v in _TEN.items()}
        self._dialect_teens = {fold(k): v for k, v in _DIALECT_TEENS.items()}
        self._tens = {fold(k): v for k, v in _TENS.items()}
        self._hundred_words = {fold(w) for w in _HUNDRED_WORDS}
        self._hundreds = {fold(k): v for k, v in _HUNDREDS.items()}
        self._multipliers = {fold(k): v for k, v in _MULTIPLIERS.items()}
        self._standalone_scales = {fold(k): v for k, v in _STANDALONE_SCALES.items()}
        self._zero = fold(_ZERO)
        self._wahid = fold("واحد")
        self._lexicon = {
            self._zero,
            *self._ones,
            *self._teen_first,
            *self._ten,
            *self._dialect_teens,
            *self._tens,
            *self._hundreds,
            *self._multipliers,
            *self._standalone_scales,
        }

    def _fold(self, word: str) -> str:
        return word.translate(self._table)

    def __call__(self, text: str) -> str:
        if not text.strip():
            return text
        toks = self._tokenize(text.split())
        out: list[str] = []
        i = 0
        while i < len(toks):
            parsed = self._parse_number(toks, i)
            single_one = (
                parsed is not None and parsed[0] == i + 1 and toks[i].word in self._ones
            )
            if parsed is None or single_one:
                out.append(toks[i].raw)
                i += 1
                continue
            end, value = parsed
            first, last = toks[i], toks[end - 1]
            out.append(f"{first.lead}{first.conj}{value}{last.trail}")
            i = end
        return " ".join(out)

    def _is_number_word(self, word: str) -> bool:
        return word in self._lexicon or (word.isascii() and word.isdigit())

    def _tokenize(self, words: list[str]) -> list[_Token]:
        toks: list[_Token] = []
        i = 0
        while i < len(words):
            raw = words[i]
            lead, word, trail = self._split(raw)
            next_word = self._split(words[i + 1])[1] if i + 1 < len(words) else ""
            # "وأحد" folds to "واحد"; after a number and before عشر it is و + أحد
            # (مئة وأحد عشر = 111), since "واحد عشر" is not a valid teen.
            is_and_ahad = (
                word == self._wahid
                and next_word in self._ten
                and bool(toks)
                and toks[-1].word is not None
            )
            if self._is_number_word(word) and not is_and_ahad:
                toks.append(_Token(raw, lead, trail, word))
            elif (
                word.startswith(_CONJUNCTION)
                and not lead
                and self._is_number_word(word[1:])
            ):
                toks.append(_Token(raw, lead, trail, word[1:], _CONJUNCTION))
            elif word == _CONJUNCTION and not lead and not trail and next_word:
                next_lead, _, next_trail = self._split(words[i + 1])
                if next_lead or next_word not in self._lexicon:
                    toks.append(_Token(raw))
                else:
                    merged = f"{raw} {words[i + 1]}"
                    conj = f"{_CONJUNCTION} "
                    toks.append(_Token(merged, "", next_trail, next_word, conj))
                    i += 1
            else:
                toks.append(_Token(raw))
            i += 1
        return toks

    def _split(self, raw: str) -> tuple[str, str, str]:
        """Fold a raw token and split it into (leading punct, word, trailing punct)."""
        match = _RE_PUNCT_EDGES.match(self._fold(raw))
        assert match is not None
        return match.group(1), match.group(2), match.group(3)

    @staticmethod
    def _joinable(toks: list[_Token], i: int) -> bool:
        """Whether toks[i] can continue the number ending at toks[i - 1]."""
        return i < len(toks) and not toks[i - 1].trail and not toks[i].lead

    def _parse_number(self, toks: list[_Token], i: int) -> tuple[int, int] | None:
        term = self._parse_term(toks, i)
        if term is None:
            return None
        end, total, scale = term
        # Larger groups are followed by smaller ones: ألف وتسعمائة وتسعين.
        while scale > 1 and self._joinable(toks, end) and toks[end].conj:
            nxt = self._parse_term(toks, end)
            if nxt is None or nxt[2] >= scale:
                break
            end, value, scale = nxt
            total += value
        return end, total

    def _parse_term(self, toks: list[_Token], i: int) -> tuple[int, int, int] | None:
        """Parse one scale group; returns (end, value, scale)."""
        word = toks[i].word
        if word is None:
            return None
        if word in self._standalone_scales:
            value, scale = self._standalone_scales[word]
            return i + 1, value, scale
        if word.isascii() and word.isdigit():
            j = i + 1
            if self._is_multiplier(toks, j):
                mult = self._multipliers[toks[j].word or ""]
                return j + 1, int(word) * mult, mult
            return None
        parsed = self._parse_below_1000(toks, i)
        if parsed is None:
            return None
        j, value = parsed
        if self._is_multiplier(toks, j):
            mult = self._multipliers[toks[j].word or ""]
            return j + 1, value * mult, mult
        return j, value, 1

    def _is_multiplier(self, toks: list[_Token], j: int) -> bool:
        return (
            self._joinable(toks, j)
            and not toks[j].conj
            and toks[j].word in self._multipliers
        )

    def _parse_below_1000(self, toks: list[_Token], i: int) -> tuple[int, int] | None:
        word = toks[i].word
        if word in self._hundreds:
            hundreds, j = self._hundreds[word], i + 1
        elif (
            word in self._units
            and self._joinable(toks, i + 1)
            and not toks[i + 1].conj
            and toks[i + 1].word in self._hundred_words
        ):
            hundreds, j = self._units[word] * 100, i + 2
        else:
            return self._parse_below_100(toks, i)
        if self._joinable(toks, j) and toks[j].conj:
            rest = self._parse_below_100(toks, j)
            if rest is not None:
                return rest[0], hundreds + rest[1]
        return j, hundreds

    def _parse_below_100(self, toks: list[_Token], i: int) -> tuple[int, int] | None:
        word = toks[i].word
        if word is None:
            return None
        if word in self._dialect_teens:
            return i + 1, self._dialect_teens[word]
        if (
            word in self._teen_first
            and self._joinable(toks, i + 1)
            and not toks[i + 1].conj
            and toks[i + 1].word in self._ten
        ):
            return i + 2, 10 + self._teen_first[word]
        if word in self._tens:
            return i + 1, self._tens[word]
        unit = self._units.get(word, self._ones.get(word))
        if unit is not None:
            nxt = i + 1
            if self._joinable(toks, nxt) and toks[nxt].conj:
                tens = self._tens.get(toks[nxt].word or "")
                if tens is not None:
                    return nxt + 1, unit + tens
            return nxt, unit
        if word in self._ten:
            return i + 1, 10
        if word == self._zero:
            return i + 1, 0
        return None
