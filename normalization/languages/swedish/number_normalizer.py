"""Swedish number normalizer (STT-oriented).

``text2num.alpha2digit`` does not support Swedish, so this module implements
spelled-out cardinal parsing for common transcript patterns: 0–999, ``tusen``
compounds, and large multipliers (``miljon``, ``miljard``, ``biljon``).
Optionally rewrites currency symbols like the Dutch normalizer, then restores
plural currency words from config.
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
    "två": 2,
    "tre": 3,
    "fyra": 4,
    "fem": 5,
    "sex": 6,
    "sju": 7,
    "åtta": 8,
    "atta": 8,
    "nio": 9,
}

_TEENS: dict[str, int] = {
    "tio": 10,
    "elva": 11,
    "tolv": 12,
    "tretton": 13,
    "fjorton": 14,
    "femton": 15,
    "sexton": 16,
    "sjutton": 17,
    "arton": 18,
    "aderton": 18,
    "nitton": 19,
}

_TENS: dict[str, int] = {
    "tjugo": 20,
    "trettio": 30,
    "fyrtio": 40,
    "femtio": 50,
    "sextio": 60,
    "sjuttio": 70,
    "åttio": 80,
    "attio": 80,
    "nittio": 90,
}

_TENS_PREFIXES: tuple[tuple[str, int], ...] = tuple(_TENS.items())

_ONES_AFTER_TENS: dict[str, int] = {"ett": 1, "en": 1, **_ONES_2_9}

_DIGIT_TO_SWEDISH: dict[str, str] = {
    "0": "noll",
    "1": "ett",
    "2": "två",
    "3": "tre",
    "4": "fyra",
    "5": "fem",
    "6": "sex",
    "7": "sju",
    "8": "åtta",
    "9": "nio",
}

_RE_MIXED_NUMBER = re.compile(
    r"\b(\d+)\s+("
    r"miljon|miljoner|miljard|miljarder|biljon|biljoner|tusen"
    r")\b",
    re.IGNORECASE,
)

_BIG_MULT: dict[str, int] = {
    "tusen": 1000,
    "miljon": 1_000_000,
    "miljoner": 1_000_000,
    "miljard": 1_000_000_000,
    "miljarder": 1_000_000_000,
    "biljon": 1_000_000_000_000,
    "biljoner": 1_000_000_000_000,
}


def _normalize_mixed_numbers(text: str) -> str:
    """Convert ``3 miljard`` → ``tre miljard`` so the word parser yields 3e9."""

    def replace(match: re.Match[str]) -> str:
        number = match.group(1)
        multiplier = match.group(2)
        if len(number) == 1 and number in _DIGIT_TO_SWEDISH:
            return f"{_DIGIT_TO_SWEDISH[number]} {multiplier}"
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
    if t == "kronor":
        return "krona"
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
        elif tl == "kronor":
            pat = re.compile(rf"\b{amount}\s+krona\b", re.IGNORECASE)
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
    if _fold(word) in ("en", "ett"):
        return 1
    return _get(_ONES_2_9, word)


class SwedishNumberNormalizer:
    """Convert Swedish spelled-out numbers to digits."""

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

        if fw == "tusen":
            tail = self._parse_number(words, i + 1, n)
            if tail is not None:
                end, v2 = tail
                return end, 1000 + v2
            return i + 1, 1000

        if i + 1 < n and fw in ("en", "ett") and _fold(words[i + 1]) == "tusen":
            tail = self._parse_number(words, i + 2, n)
            base = 1000
            if tail is not None:
                end, v2 = tail
                return end, base + v2
            return i + 2, base

        if i + 1 < n and fw in ("en", "ett") and _fold(words[i + 1]) == "miljon":
            tail = self._parse_number(words, i + 2, n)
            base = 1_000_000
            if tail is not None:
                end, v2 = tail
                return end, base + v2
            return i + 2, base

        if (
            i + 1 < n
            and fw in ("en", "ett")
            and _fold(words[i + 1])
            in (
                "miljard",
                "miljarder",
            )
        ):
            tail = self._parse_number(words, i + 2, n)
            base = 1_000_000_000
            if tail is not None:
                end, v2 = tail
                return end, base + v2
            return i + 2, base

        if (
            i + 1 < n
            and fw in ("en", "ett")
            and _fold(words[i + 1])
            in (
                "biljon",
                "biljoner",
            )
        ):
            tail = self._parse_number(words, i + 2, n)
            base = 1_000_000_000_000
            if tail is not None:
                end, v2 = tail
                return end, base + v2
            return i + 2, base

        sub999 = self._parse_0_999(words, i, n)
        if sub999 is None:
            return None
        j, v = sub999
        if j >= n:
            return j, v

        next_fw = _fold(words[j])
        if next_fw == "tusen":
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

        if _fold(words[i]) == "noll":
            if i + 1 < n and self._continues_number(words[i + 1]):
                return None
            return i + 1, 0

        if _fold(words[i]) == "hundra":
            tail = self._parse_0_99(words, i + 1, n)
            if tail is not None:
                je, tv = tail
                return je, 100 + tv
            return i + 1, 100

        if i + 1 < n and _fold(words[i + 1]) == "hundra":
            m = _hundred_multiplier(words[i])
            if m is None:
                return None
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
        if fw == "hundra" or fw == "tusen":
            return True
        if fw in _BIG_MULT:
            return True
        if _get(_TEENS, word) is not None:
            return True
        if _get(_TENS, word) is not None:
            return True
        if _get(_ONES_2_9, word) is not None:
            return True
        if fw in ("en", "ett"):
            return True
        return False

    def _parse_0_99(self, words: list[str], i: int, n: int) -> tuple[int, int] | None:
        if i >= n:
            return None

        fw = _fold(words[i])

        v = _get(_TEENS, words[i])
        if v is not None:
            return i + 1, v

        for prefix, tval in _TENS_PREFIXES:
            pl = len(prefix)
            if fw.startswith(prefix) and len(fw) > pl:
                rest = fw[pl:]
                unit = _get(_ONES_AFTER_TENS, rest)
                if unit is not None:
                    return i + 1, tval + unit

        tens = _get(_TENS, words[i])
        if tens is not None:
            j = i + 1
            if j < n:
                nfw = _fold(words[j])
                if nfw in ("ett", "en"):
                    return j + 1, tens + 1
                o = _get(_ONES_2_9, words[j])
                if o is not None:
                    return j + 1, tens + o
            return i + 1, tens

        o = _get(_ONES_2_9, words[i])
        if o is not None:
            return i + 1, o

        if fw in ("en", "ett"):
            return None

        return None
