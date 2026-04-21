"""Dutch number normalizer using text2num's alpha2digit.

Converts spelled-out numbers to digits (e.g. vijf en twintig → 25) and handles
mixed digit+word forms (e.g. 3 miljard → drie miljard) before conversion so
alpha2digit does not misinterpret them. Optionally rewrites currency symbols to
amount + spoken singular unit, then restores plural trailing words from config.
"""

import re

from text_to_num import alpha2digit

# Digit-to-Dutch-word mapping for normalizing "3 miljard" → "drie miljard".
_DIGIT_TO_DUTCH: dict[str, str] = {
    "0": "nul",
    "1": "een",
    "2": "twee",
    "3": "drie",
    "4": "vier",
    "5": "vijf",
    "6": "zes",
    "7": "zeven",
    "8": "acht",
    "9": "negen",
}

# Pattern: digit(s) followed by Dutch large-number multipliers.
_RE_MIXED_NUMBER = re.compile(
    r"\b(\d+)\s+(miljoen|miljoenen|miljard|miljarden|biljoen|biljoenen)\b",
    re.IGNORECASE,
)


def _normalize_mixed_numbers(text: str) -> str:
    """Convert '3 miljard' → 'drie miljard' so alpha2digit yields 3e9, not '3 1000000000'.

    alpha2digit may concatenate a lone digit with the following word; converting
    the digit to a word avoids that (e.g. 'drie miljard' → 3000000000).
    """

    def replace(match: re.Match) -> str:
        number = match.group(1)
        multiplier = match.group(2)
        if len(number) == 1 and number in _DIGIT_TO_DUTCH:
            return f"{_DIGIT_TO_DUTCH[number]} {multiplier}"
        # Multi-digit: keep as-is; alpha2digit will handle or leave unchanged
        return match.group(0)

    return _RE_MIXED_NUMBER.sub(replace, text)


def _singular_spoken_unit(trailing_word: str) -> str:
    """Map ``currency_symbol_to_word`` value to a spoken singular alpha2digit accepts."""
    t = trailing_word.lower()
    if t == "euros":
        return "euro"
    if t == "dollars":
        return "dollar"
    if t == "ponden":
        return "pond"
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
        text = re.sub(rf"{esc}\s*({num})", rf"\1 {singular}", text, flags=re.IGNORECASE)
        text = re.sub(rf"({num})\s*{esc}", rf"\1 {singular}", text, flags=re.IGNORECASE)
    return text


def _currency_plural_fix_patterns(
    currency_symbol_to_word: dict[str, str] | None,
) -> tuple[tuple[re.Pattern[str], str], ...]:
    """Build (pattern, replacement) pairs so digit + alpha2digit singular → config trailing word."""
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


class DutchNumberNormalizer:
    """Convert Dutch spelled-out numbers to digits via text2num.alpha2digit.

    Applies pre-passes for currency symbols (when configured) and mixed digit+word
    forms (e.g. 3 miljard) before calling alpha2digit, then normalizes currency
    words to the plural forms in ``currency_symbol_to_word``.
    """

    def __init__(self, currency_symbol_to_word: dict[str, str] | None = None) -> None:
        if alpha2digit is None:
            raise ImportError(
                "Dutch number normalization requires the text2num package. "
                "Install it with: uv add text2num"
            )
        self._alpha2digit = alpha2digit
        self._currency_symbol_to_word = currency_symbol_to_word
        self._currency_plural_fixes = _currency_plural_fix_patterns(
            currency_symbol_to_word,
        )

    def __call__(self, text: str) -> str:
        text = _normalize_currency_symbols(text, self._currency_symbol_to_word)
        text = _normalize_mixed_numbers(text)
        text = self._alpha2digit(text, "nl")
        text = _apply_currency_plural_fixes(text, self._currency_plural_fixes)
        return text
