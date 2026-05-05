"""Finnish number normalizer (STT-oriented).

Finnish is not supported by ``text2num.alpha2digit``, so this module parses
common transcript-style cardinals: 0–999 (including ``kymmentä`` tens),
``tuhat`` / ``tuhatta``, and large multipliers (``miljoona``, ``miljardi``,
``biljoona``). Optionally rewrites currency symbols like the Dutch/Swedish
normalizers, then restores plural currency words from config.
"""

from __future__ import annotations

import re


def _fold(s: str) -> str:
    return s.lower()


def _get(table: dict[str, int], word: str) -> int | None:
    fw = _fold(word)
    for k, v in table.items():
        if _fold(k) == fw:
            return v
    return None


_ONES_2_9: dict[str, int] = {
    "kaksi": 2,
    "kolme": 3,
    "neljä": 4,
    "nelja": 4,
    "viisi": 5,
    "kuusi": 6,
    "seitsemän": 7,
    "seitseman": 7,
    "kahdeksan": 8,
    "yhdeksän": 9,
    "yhdeksan": 9,
}

_ONES_1_9: dict[str, int] = {
    "yksi": 1,
    **_ONES_2_9,
}

_MULT_BEFORE_KYM: dict[str, int] = {
    "yksi": 1,
    "kaksi": 2,
    "kolme": 3,
    "neljä": 4,
    "nelja": 4,
    "viisi": 5,
    "kuusi": 6,
    "seitsemän": 7,
    "seitseman": 7,
    "kahdeksan": 8,
    "yhdeksän": 9,
    "yhdeksan": 9,
}

_TEENS: dict[str, int] = {
    "kymmenen": 10,
    "yksitoista": 11,
    "kaksitoista": 12,
    "kolmetoista": 13,
    "neljätoista": 14,
    "neljatoista": 14,
    "viisitoista": 15,
    "kuusitoista": 16,
    "seitsemäntoista": 17,
    "seitsemantoista": 17,
    "kahdeksantoista": 18,
    "yhdeksäntoista": 19,
    "yhdeksantoista": 19,
}

_KYMENTTA = "kymmentä"
_KYMENTTA_ASCII = "kymmenta"


def _parse_glued_kymmenta(word: str) -> tuple[int, int] | None:
    """Parse a single token like ``kaksikymmentäviisi`` → (25, consumed)."""
    fw = _fold(word)
    key = _KYMENTTA
    if key not in fw:
        key = _KYMENTTA_ASCII
        if key not in fw:
            return None
    idx = fw.index(key)
    left = fw[:idx]
    right = fw[idx + len(key) :]
    tens_m = _get(_MULT_BEFORE_KYM, left)
    if tens_m is None:
        return None
    base = tens_m * 10
    if not right:
        return base, 1
    unit = _get(_ONES_1_9, right)
    if unit is None:
        return None
    return base + unit, 1


_DIGIT_TO_FINNISH: dict[str, str] = {
    "0": "nolla",
    "1": "yksi",
    "2": "kaksi",
    "3": "kolme",
    "4": "neljä",
    "5": "viisi",
    "6": "kuusi",
    "7": "seitsemän",
    "8": "kahdeksan",
    "9": "yhdeksän",
}

_RE_MIXED_NUMBER = re.compile(
    r"\b(\d+)\s+("
    r"miljoona|miljoonaa|miljoonan|"
    r"miljardi|miljardia|miljardin|"
    r"biljoona|biljoonaa|biljoonan|"
    r"tuhat|tuhatta"
    r")\b",
    re.IGNORECASE,
)

_BIG_MULT: dict[str, int] = {
    "tuhat": 1000,
    "tuhatta": 1000,
    "miljoona": 1_000_000,
    "miljoonaa": 1_000_000,
    "miljoonan": 1_000_000,
    "miljardi": 1_000_000_000,
    "miljardia": 1_000_000_000,
    "miljardin": 1_000_000_000,
    "biljoona": 1_000_000_000_000,
    "biljoonaa": 1_000_000_000_000,
    "biljoonan": 1_000_000_000_000,
}


def _normalize_mixed_numbers(text: str) -> str:
    """Convert ``3 miljardi`` → ``kolme miljardi`` so the word parser yields 3e9."""

    def replace(match: re.Match[str]) -> str:
        number = match.group(1)
        multiplier = match.group(2)
        if len(number) == 1 and number in _DIGIT_TO_FINNISH:
            return f"{_DIGIT_TO_FINNISH[number]} {multiplier}"
        return match.group(0)

    return _RE_MIXED_NUMBER.sub(replace, text)


def _singular_spoken_unit(trailing_word: str) -> str:
    t = trailing_word.lower()
    if t == "euros":
        return "euro"
    if t == "dollars":
        return "dollar"
    if t == "pounds":
        return "pound"
    if t == "yens":
        return "yen"
    return trailing_word


def _normalize_currency_symbols(
    text: str,
    currency_symbol_to_word: dict[str, str] | None,
) -> str:
    if not currency_symbol_to_word:
        return text
    num = r"\d+(?:[.,]\d+)?"
    for symbol, trailing in currency_symbol_to_word.items():
        singular = _singular_spoken_unit(trailing)
        esc = re.escape(symbol)
        sym = rf"\b{esc}\b" if len(symbol) > 1 else esc
        text = re.sub(rf"{sym}\s*({num})", rf"\1 {singular}", text, flags=re.IGNORECASE)
        text = re.sub(rf"({num})\s*{sym}", rf"\1 {singular}", text, flags=re.IGNORECASE)
    return text


def _currency_plural_fix_patterns(
    currency_symbol_to_word: dict[str, str] | None,
) -> tuple[tuple[re.Pattern[str], str], ...]:
    if not currency_symbol_to_word:
        return ()
    amount = r"(\d+(?:[.,]\d+)?)"
    seen: set[str] = set()
    out: list[tuple[re.Pattern[str], str]] = []
    for _symbol, trailing in currency_symbol_to_word.items():
        tl = trailing.lower()
        if tl in seen:
            continue
        seen.add(tl)
        singular = _singular_spoken_unit(trailing)
        if singular.lower() == tl:
            continue
        if tl == "euros":
            pat = re.compile(rf"\b{amount}\s+euro(?:'s)?\b", re.IGNORECASE)
            out.append((pat, rf"\1 {trailing}"))
        else:
            pat = re.compile(
                rf"\b{amount}\s+{re.escape(singular)}\b",
                re.IGNORECASE,
            )
            out.append((pat, rf"\1 {trailing}"))
    return tuple(out)


def _apply_currency_plural_fixes(
    text: str,
    fixers: tuple[tuple[re.Pattern[str], str], ...],
) -> str:
    for pattern, repl in fixers:
        text = pattern.sub(repl, text)
    return text


def _hundred_multiplier(word: str) -> int | None:
    if _fold(word) == "yksi":
        return 1
    return _get(_ONES_2_9, word)


class FinnishNumberNormalizer:
    """Convert Finnish spelled-out numbers to digits."""

    def __init__(self, currency_symbol_to_word: dict[str, str] | None = None) -> None:
        self._currency_symbol_to_word = currency_symbol_to_word
        self._currency_plural_fixes = _currency_plural_fix_patterns(
            currency_symbol_to_word,
        )

    def __call__(self, text: str) -> str:
        if not text.strip():
            return text
        text = _normalize_currency_symbols(text, self._currency_symbol_to_word)
        text = _normalize_mixed_numbers(text)
        words = text.split()
        out: list[str] = []
        i = 0
        n = len(words)
        while i < n:
            parsed = self._parse_number(words, i, n)
            if parsed is not None:
                end, value = parsed
                out.append(str(value))
                i = end
            else:
                out.append(words[i])
                i += 1
        text = " ".join(out)
        text = _apply_currency_plural_fixes(text, self._currency_plural_fixes)
        return text

    def _parse_number(self, words: list[str], i: int, n: int) -> tuple[int, int] | None:
        if i >= n:
            return None

        fw = _fold(words[i])

        if fw in ("tuhat", "tuhatta"):
            j = i + 1
            tail = self._parse_number(words, j, n)
            if tail is not None:
                end, v2 = tail
                return end, 1000 + v2
            return j, 1000

        if i + 1 < n and fw == "yksi" and _fold(words[i + 1]) in ("tuhat", "tuhatta"):
            j = i + 2
            tail = self._parse_number(words, j, n)
            base = 1000
            if tail is not None:
                end, v2 = tail
                return end, base + v2
            return j, base

        if i + 1 < n and fw == "yksi" and _fold(words[i + 1]) == "miljoona":
            j = i + 2
            tail = self._parse_number(words, j, n)
            base = 1_000_000
            if tail is not None:
                end, v2 = tail
                return end, base + v2
            return j, base

        if (
            i + 1 < n
            and fw == "yksi"
            and _fold(words[i + 1])
            in (
                "miljardi",
                "miljardia",
            )
        ):
            j = i + 2
            tail = self._parse_number(words, j, n)
            base = 1_000_000_000
            if tail is not None:
                end, v2 = tail
                return end, base + v2
            return j, base

        if (
            i + 1 < n
            and fw == "yksi"
            and _fold(words[i + 1])
            in (
                "biljoona",
                "biljoonaa",
            )
        ):
            j = i + 2
            tail = self._parse_number(words, j, n)
            base = 1_000_000_000_000
            if tail is not None:
                end, v2 = tail
                return end, base + v2
            return j, base

        sub999 = self._parse_0_999(words, i, n)
        if sub999 is None:
            return None
        j, v = sub999
        if j >= n:
            return j, v

        next_fw = _fold(words[j])
        if next_fw in ("tuhat", "tuhatta"):
            j += 1
            prod = v * 1000
            if j >= n:
                return j, prod
            tail = self._parse_number(words, j, n)
            if tail is not None:
                end, v2 = tail
                return end, prod + v2
            return j, prod

        mult = _BIG_MULT.get(next_fw)
        if mult is not None and mult >= 1_000_000:
            j += 1
            prod = v * mult
            if j >= n:
                return j, prod
            tail = self._parse_number(words, j, n)
            if tail is not None:
                end, v2 = tail
                return end, prod + v2
            return j, prod

        return j, v

    def _parse_0_999(self, words: list[str], i: int, n: int) -> tuple[int, int] | None:
        if i >= n:
            return None

        if _fold(words[i]) == "nolla":
            if i + 1 < n and self._continues_number(words[i + 1]):
                return None
            return i + 1, 0

        if _fold(words[i]) == "sata":
            tail = self._parse_0_99(words, i + 1, n)
            if tail is not None:
                je, tv = tail
                return je, 100 + tv
            return i + 1, 100

        if i + 1 < n and _fold(words[i + 1]) in ("sata", "sataa"):
            m = _hundred_multiplier(words[i])
            if m is None:
                m = _get(_ONES_2_9, words[i])
            if m is None:
                return None
            next_w = _fold(words[i + 1])
            if m == 1 and next_w == "sata":
                base = 100
            else:
                base = m * 100
            j = i + 2
            tail = self._parse_0_99(words, j, n)
            if tail is not None:
                je, tv = tail
                return je, base + tv
            return j, base

        return self._parse_0_99(words, i, n)

    def _continues_number(self, word: str) -> bool:
        fw = _fold(word)
        if fw in ("sata", "sataa", "tuhat", "tuhatta"):
            return True
        if fw in _BIG_MULT:
            return True
        if _get(_TEENS, word) is not None:
            return True
        if _get(_MULT_BEFORE_KYM, word) is not None:
            return True
        if fw in (_KYMENTTA, _KYMENTTA_ASCII):
            return True
        if _get(_ONES_2_9, word) is not None:
            return True
        if fw == "yksi":
            return True
        if _parse_glued_kymmenta(word) is not None:
            return True
        return False

    def _parse_ones_1_9(
        self, words: list[str], i: int, n: int
    ) -> tuple[int, int] | None:
        if i >= n:
            return None
        v = _get(_ONES_1_9, words[i])
        if v is None or v == 0:
            return None
        return i + 1, v

    def _parse_0_99(self, words: list[str], i: int, n: int) -> tuple[int, int] | None:
        if i >= n:
            return None

        glued = _parse_glued_kymmenta(words[i])
        if glued is not None:
            val, consumed = glued
            return i + consumed, val

        v = _get(_TEENS, words[i])
        if v is not None:
            return i + 1, v

        fw = _fold(words[i])
        if i + 1 < n:
            nxt = _fold(words[i + 1])
            if nxt in (_KYMENTTA, _KYMENTTA_ASCII):
                tens_m = _get(_MULT_BEFORE_KYM, words[i])
                if tens_m is not None:
                    base = tens_m * 10
                    j = i + 2
                    ones = self._parse_ones_1_9(words, j, n)
                    if ones is not None:
                        je, ov = ones
                        return je, base + ov
                    return j, base

        v = _get(_ONES_2_9, words[i])
        if v is not None:
            return i + 1, v

        if fw == "yksi":
            return i + 1, 1

        return None
