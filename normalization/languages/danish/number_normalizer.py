"""Danish number normalizer (STT-oriented).

``text2num.alpha2digit`` does not support Danish, so this module implements
spelled-out cardinal parsing for common transcript patterns: 0–999, ``tusind``
compounds, and large multipliers (``million``, ``milliard``, ``billion``).
Danish uses the vigesimal (base-20) system for 50–90 and forms compound numbers
as ``"X og Y"`` (e.g. ``"en og tyve"`` = 21) or as glued words (``"enogtyve"``).
Optionally rewrites currency symbols then restores plural currency words from config.
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
    "to": 2,
    "tre": 3,
    "fire": 4,
    "fem": 5,
    "seks": 6,
    "syv": 7,
    "otte": 8,
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
    "tyve": 20,
    "tredive": 30,
    "tredve": 30,  # colloquial spoken variant
    "fyrre": 40,
    "halvtreds": 50,
    "tres": 60,
    "halvfjerds": 70,
    "firs": 80,
    "halvfems": 90,
}

# In Danish the ordinal indicator is a trailing period, e.g. "første" → "1."
_ORDINALS: dict[str, tuple[int, str]] = {
    "første": (1, "."),
    "anden": (2, "."),
    "tredje": (3, "."),
    "fjerde": (4, "."),
    "femte": (5, "."),
    "sjette": (6, "."),
    "syvende": (7, "."),
    "ottende": (8, "."),
    "niende": (9, "."),
    "tiende": (10, "."),

    "ellevte": (11, "."),
    "tolvte": (12, "."),
    "trettende": (13, "."),
    "fjortende": (14, "."),
    "femtende": (15, "."),
    "sekstende": (16, "."),
    "syttende": (17, "."),
    "attende": (18, "."),
    "nittende": (19, "."),

    "tyvende": (20, "."),
    "tredivte": (30, "."),
    "fyrrende": (40, "."),
    "fyrretyvende": (40, "."),
    "halvtredsinde": (50, "."),
    "halvtredsindstyvende": (50, "."),
    "tressende": (60, "."),
    "tresindstyvende": (60, "."),
    "halvfjerdsende": (70, "."),
    "halvfjerdsindtyvende": (70, "."),
    "firsende": (80, "."),
    "firsindtyvende": (80, "."),
    "halvfemsende": (90, "."),
    "halvfemsindstyvende": (90, ".")
}

_TENS_ORDINAL: dict[str, tuple[int, str]] = {
    k: v for k, v in _ORDINALS.items() if v[0] >= 20
}

# Used for og-compound ones part (includes en/et = 1 alongside 2-9)
_ONES_FOR_OG: dict[str, int] = {"en": 1, "et": 1, **_ONES_2_9}

_DIGIT_TO_DANISH: dict[str, str] = {
    "0": "nul",
    "1": "en",
    "2": "to",
    "3": "tre",
    "4": "fire",
    "5": "fem",
    "6": "seks",
    "7": "syv",
    "8": "otte",
    "9": "ni",
}

_RE_MIXED_NUMBER = re.compile(
    r"\b(\d+)\s+("
    r"milliard|milliarder|million|millioner|billion|billioner|tusind"
    r")\b",
    re.IGNORECASE,
)

_BIG_MULT: dict[str, int] = {
    "tusind": 1_000,
    "tusinde": 1_000,
    "million": 1_000_000,
    "millioner": 1_000_000,
    "milliard": 1_000_000_000,
    "milliarder": 1_000_000_000,
    "billion": 1_000_000_000_000,
    "billioner": 1_000_000_000_000,
}

# Sorted longest-first so "otte" is tried before "et" etc. in glued-compound detection.
_ONES_FOR_OG_SORTED: tuple[tuple[str, int], ...] = tuple(
    sorted(_ONES_FOR_OG.items(), key=lambda kv: len(kv[0]), reverse=True)
)


def _try_parse_og_compound(word: str) -> int | None:
    """Parse a glued Danish ones-og-tens compound like ``'enogtyve'`` = 21."""
    fw = _fold(word)
    for ones_str, ones_val in _ONES_FOR_OG_SORTED:
        prefix = ones_str + "og"
        if fw.startswith(prefix):
            rest = fw[len(prefix) :]
            tens_val = _TENS.get(rest)
            if tens_val is not None:
                return tens_val + ones_val
    return None


def _try_parse_og_compound_ordinal(word: str) -> tuple[int, str] | None:
    """Parse a glued Danish ordinal compound like ``'enogtyvende'`` = 21."""
    fw = _fold(word)
    for ones_str, ones_val in _ONES_FOR_OG_SORTED:
        prefix = ones_str + "og"
        if fw.startswith(prefix):
            rest = fw[len(prefix) :]
            tens = _TENS_ORDINAL.get(rest)
            if tens is not None:
                tens_val, suffix = tens
                return tens_val + ones_val, suffix
    return None


def _normalize_mixed_numbers(text: str) -> str:
    """Convert ``3 milliard`` → ``tre milliard`` so the word parser yields 3 000 000 000."""

    def replace(match: re.Match[str]) -> str:
        number = match.group(1)
        multiplier = match.group(2)
        if len(number) == 1 and number in _DIGIT_TO_DANISH:
            return f"{_DIGIT_TO_DANISH[number]} {multiplier}"
        return match.group(0)

    return _RE_MIXED_NUMBER.sub(replace, text)


def _singular_spoken_unit(trailing_word: str) -> str:
    t = trailing_word.lower()
    if t == "kroner":
        return "krone"
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
        if tl == "kroner":
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
    if _fold(word) in ("en", "et"):
        return 1
    return _get(_ONES_2_9, word)


class DanishNumberNormalizer:
    """Convert Danish spelled-out numbers to digits."""

    def __init__(self, currency_symbol_to_word: dict[str, str] | None = None) -> None:
        self._currency_symbol_to_word = currency_symbol_to_word
        self._currency_plural_fixes = _currency_plural_fix_patterns(
            currency_symbol_to_word
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
                # After parsing a cardinal, peek at the next word to see if it
                # is an ordinal continuation (e.g. "hundrede" + "enogtyvende" → 121.)
                if end < n:
                    ordinal = _ORDINALS.get(_fold(words[end]))
                    if ordinal is None:
                        ordinal = _try_parse_og_compound_ordinal(words[end])
                    if ordinal is not None:
                        ord_val, suffix = ordinal
                        out.append(str(value + ord_val) + suffix)
                        i = end + 1
                        continue
                out.append(str(value))
                i = end
            else:
                # No cardinal — check if the word is a standalone ordinal
                # (e.g. "første" → "1.", "enogtyvende" → "21.")
                ordinal = _ORDINALS.get(_fold(words[i]))
                if ordinal is None:
                    ordinal = _try_parse_og_compound_ordinal(words[i])
                if ordinal is not None:
                    ord_val, suffix = ordinal
                    out.append(str(ord_val) + suffix)
                    i += 1
                    continue
                out.append(words[i])
                i += 1
        text = " ".join(out)
        text = _apply_currency_plural_fixes(text, self._currency_plural_fixes)
        return text

    def _parse_number(self, words: list[str], i: int, n: int) -> tuple[int, int] | None:
        if i >= n:
            return None

        fw = _fold(words[i])

        if fw in ("tusind", "tusinde"):
            tail = self._parse_number(words, i + 1, n)
            if tail is not None:
                end, v2 = tail
                return end, 1000 + v2
            return i + 1, 1000

        if i + 1 < n and fw in ("en", "et") and _fold(words[i + 1]) in ("tusind", "tusinde"):
            tail = self._parse_number(words, i + 2, n)
            base = 1000
            if tail is not None:
                end, v2 = tail
                return end, base + v2
            return i + 2, base

        if (
            i + 1 < n
            and fw in ("en", "et")
            and _fold(words[i + 1])
            in (
                "million",
                "millioner",
            )
        ):
            tail = self._parse_number(words, i + 2, n)
            base = 1_000_000
            if tail is not None:
                end, v2 = tail
                return end, base + v2
            return i + 2, base

        if (
            i + 1 < n
            and fw in ("en", "et")
            and _fold(words[i + 1])
            in (
                "milliard",
                "milliarder",
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
            and fw in ("en", "et")
            and _fold(words[i + 1])
            in (
                "billion",
                "billioner",
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
        if next_fw in ("tusind", "tusinde"):
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

        fw = _fold(words[i])

        if fw == "nul":
            if i + 1 < n and self._continues_number(words[i + 1]):
                return None
            return i + 1, 0

        if fw == "hundrede":
            j = i + 1
            if j < n and _fold(words[j]) == "og":
                j += 1
            tail = self._parse_0_99_after_og(words, j, n)
            if tail is not None:
                je, tv = tail
                return je, 100 + tv
            return i + 1, 100

        if i + 1 < n and _fold(words[i + 1]) == "hundrede":
            m = _hundred_multiplier(words[i])
            if m is None:
                return None
            base = m * 100
            j = i + 2
            if j < n and _fold(words[j]) == "og":
                j += 1
            tail = self._parse_0_99_after_og(words, j, n)
            if tail is not None:
                je, tv = tail
                return je, base + tv
            return j, base

        return self._parse_0_99(words, i, n)

    def _continues_number(self, word: str) -> bool:
        fw = _fold(word)
        if fw in ("hundrede", "tusind", "tusinde"):
            return True
        if fw in _BIG_MULT:
            return True
        if _get(_TEENS, word) is not None:
            return True
        if _get(_TENS, word) is not None:
            return True
        if _get(_ONES_2_9, word) is not None:
            return True
        if fw in ("en", "et"):
            return True
        return False

    def _parse_0_99_after_og(
        self, words: list[str], i: int, n: int
    ) -> tuple[int, int] | None:
        """Parse 0–99, additionally accepting standalone ``en``/``et`` as 1 after ``og``."""
        result = self._parse_0_99(words, i, n)
        if result is not None:
            return result
        if i < n and _fold(words[i]) in ("en", "et"):
            return i + 1, 1
        return None

    def _parse_0_99(self, words: list[str], i: int, n: int) -> tuple[int, int] | None:
        if i >= n:
            return None

        fw = _fold(words[i])

        compound = _try_parse_og_compound(words[i])
        if compound is not None:
            return i + 1, compound

        v = _get(_TEENS, words[i])
        if v is not None:
            return i + 1, v

        tens = _get(_TENS, words[i])
        if tens is not None:
            return i + 1, tens

        # Three-word og-compound: "en og tyve" = 21
        ones_val = _ONES_FOR_OG.get(fw)
        if ones_val is not None and i + 2 < n and _fold(words[i + 1]) == "og":
            tens_val = _get(_TENS, words[i + 2])
            if tens_val is not None:
                return i + 3, tens_val + ones_val

        o = _get(_ONES_2_9, words[i])
        if o is not None:
            return i + 1, o

        # Standalone "en"/"et" → do not convert (would be article in normal prose)
        return None
