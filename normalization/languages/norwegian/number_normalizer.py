"""Norwegian (Bokmål) number normalizer (STT-oriented).

``text2num.alpha2digit`` does not cover Norwegian well for transcript-style
cardinals, so this module mirrors the Swedish approach: 0–999, ``tusen``
compounds, and large multipliers (``million``, ``milliard``, ``billion``).
Optionally rewrites currency symbols, then restores plural currency words from
config. Supports optional ``og`` between number parts (e.g. ``tjue og fem``).
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


def _skip_optional_og(words: list[str], j: int, n: int) -> int:
    if j < n and _fold(words[j]) == "og":
        return j + 1
    return j


_ONES_2_9: dict[str, int] = {
    "to": 2,
    "tre": 3,
    "fire": 4,
    "fem": 5,
    "seks": 6,
    "sju": 7,
    "syv": 7,
    "åtte": 8,
    "atte": 8,
    "ni": 9,
}

_TEENS: dict[str, int] = {
    "ti": 10,
    "elleve": 11,
    "tolv": 12,
    "tretten": 13,
    "fjorten": 14,
    "femten": 15,
    "seksten": 16,
    "sytten": 17,
    "atten": 18,
    "nitten": 19,
}

_TENS: dict[str, int] = {
    "tjue": 20,
    "tyve": 20,
    "tretti": 30,
    "førti": 40,
    "forti": 40,
    "femti": 50,
    "seksti": 60,
    "sytti": 70,
    "åtti": 80,
    "atti": 80,
    "nitti": 90,
}

_TENS_PREFIXES: tuple[tuple[str, int], ...] = tuple(
    sorted(_TENS.items(), key=lambda kv: len(kv[0]), reverse=True)
)

_ONES_AFTER_TENS: dict[str, int] = {"ett": 1, "en": 1, "ein": 1, **_ONES_2_9}

_DIGIT_TO_NORWEGIAN: dict[str, str] = {
    "0": "null",
    "1": "en",
    "2": "to",
    "3": "tre",
    "4": "fire",
    "5": "fem",
    "6": "seks",
    "7": "sju",
    "8": "åtte",
    "9": "ni",
}

_RE_MIXED_NUMBER = re.compile(
    r"\b(\d+)\s+("
    r"million|millioner|milliard|milliarder|billion|billioner|tusen"
    r")\b",
    re.IGNORECASE,
)

_BIG_MULT: dict[str, int] = {
    "tusen": 1000,
    "million": 1_000_000,
    "millioner": 1_000_000,
    "milliard": 1_000_000_000,
    "milliarder": 1_000_000_000,
    "billion": 1_000_000_000_000,
    "billioner": 1_000_000_000_000,
}


def _normalize_mixed_numbers(text: str) -> str:
    """Convert ``3 milliard`` → ``tre milliard`` so the word parser yields 3e9."""

    def replace(match: re.Match[str]) -> str:
        number = match.group(1)
        multiplier = match.group(2)
        if len(number) == 1 and number in _DIGIT_TO_NORWEGIAN:
            return f"{_DIGIT_TO_NORWEGIAN[number]} {multiplier}"
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
    if t == "kroner":
        return "krone"
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
        elif tl == "kroner":
            pat = re.compile(rf"\b{amount}\s+krone\b", re.IGNORECASE)
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
    if _fold(word) in ("en", "ett", "ein"):
        return 1
    return _get(_ONES_2_9, word)


class NorwegianNumberNormalizer:
    """Convert Norwegian spelled-out numbers to digits."""

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
            j = _skip_optional_og(words, i + 1, n)
            tail = self._parse_number(words, j, n)
            if tail is not None:
                end, v2 = tail
                return end, 1000 + v2
            return j, 1000

        if i + 1 < n and fw in ("en", "ett", "ein") and _fold(words[i + 1]) == "tusen":
            j = i + 2
            j = _skip_optional_og(words, j, n)
            tail = self._parse_number(words, j, n)
            base = 1000
            if tail is not None:
                end, v2 = tail
                return end, base + v2
            return j, base

        if (
            i + 1 < n
            and fw in ("en", "ett", "ein")
            and _fold(words[i + 1]) == "million"
        ):
            j = i + 2
            j = _skip_optional_og(words, j, n)
            tail = self._parse_number(words, j, n)
            base = 1_000_000
            if tail is not None:
                end, v2 = tail
                return end, base + v2
            return j, base

        if (
            i + 1 < n
            and fw in ("en", "ett", "ein")
            and _fold(words[i + 1])
            in (
                "milliard",
                "milliarder",
            )
        ):
            j = i + 2
            j = _skip_optional_og(words, j, n)
            tail = self._parse_number(words, j, n)
            base = 1_000_000_000
            if tail is not None:
                end, v2 = tail
                return end, base + v2
            return j, base

        if (
            i + 1 < n
            and fw in ("en", "ett", "ein")
            and _fold(words[i + 1])
            in (
                "billion",
                "billioner",
            )
        ):
            j = i + 2
            j = _skip_optional_og(words, j, n)
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
        if next_fw == "tusen":
            j += 1
            j = _skip_optional_og(words, j, n)
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
            j = _skip_optional_og(words, j, n)
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

        if _fold(words[i]) == "null":
            if i + 1 < n and self._continues_number(words[i + 1]):
                return None
            return i + 1, 0

        if _fold(words[i]) == "hundre":
            j = _skip_optional_og(words, i + 1, n)
            tail = self._parse_0_99(words, j, n)
            if tail is not None:
                je, tv = tail
                return je, 100 + tv
            return i + 1, 100

        if i + 1 < n and _fold(words[i + 1]) == "hundre":
            m = _hundred_multiplier(words[i])
            if m is None:
                return None
            base = m * 100
            j = i + 2
            j = _skip_optional_og(words, j, n)
            tail = self._parse_0_99(words, j, n)
            if tail is not None:
                je, tv = tail
                return je, base + tv
            return j, base

        return self._parse_0_99(words, i, n)

    def _continues_number(self, word: str) -> bool:
        fw = _fold(word)
        if fw == "og":
            return True
        if fw == "hundre" or fw == "tusen":
            return True
        if fw in _BIG_MULT:
            return True
        if _get(_TEENS, word) is not None:
            return True
        if _get(_TENS, word) is not None:
            return True
        if _get(_ONES_2_9, word) is not None:
            return True
        if fw in ("en", "ett", "ein"):
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
            j = _skip_optional_og(words, j, n)
            if j < n:
                nfw = _fold(words[j])
                if nfw in ("ett", "en", "ein"):
                    return j + 1, tens + 1
                o = _get(_ONES_2_9, words[j])
                if o is not None:
                    return j + 1, tens + o
            return i + 1, tens

        o = _get(_ONES_2_9, words[i])
        if o is not None:
            return i + 1, o

        if fw in ("en", "ett", "ein"):
            return None

        return None
