"""Portuguese number normalizer using text2num's alpha2digit.

Converts spelled-out numbers to digits (e.g. vinte e tres → 23) and expands
mixed digit+multiplier forms (e.g. 25 mil → 25000) before conversion.
"""

import re
import unicodedata

from text_to_num import alpha2digit

_RE_MIXED_NUMBER = re.compile(
    r"\b(\d+)\s+(mil|milhao|milhoes|milhão|milhões|bilhao|bilhoes|bilhão|bilhões)\b",
    re.IGNORECASE,
)

# text2num expects accented Portuguese forms; STT often drops accents.
_UNACCENTED_NUMBER_FORMS: dict[str, str] = {
    "milhoes": "milhões",
    "milhao": "milhão",
    "bilhoes": "bilhões",
    "bilhao": "bilhão",
    "tres": "três",
}

_MULTIPLIER_SCALE: dict[str, int] = {
    "mil": 1_000,
    "milhao": 1_000_000,
    "milhoes": 1_000_000,
    "milhão": 1_000_000,
    "milhões": 1_000_000,
    "bilhao": 1_000_000_000,
    "bilhoes": 1_000_000_000,
    "bilhão": 1_000_000_000,
    "bilhões": 1_000_000_000,
}


def _fold_accents(word: str) -> str:
    lowered = word.lower()
    return "".join(
        c for c in unicodedata.normalize("NFD", lowered) if unicodedata.category(c) != "Mn"
    )


def _multiplier_scale(multiplier_word: str) -> int | None:
    folded = _fold_accents(multiplier_word)
    for key, scale in _MULTIPLIER_SCALE.items():
        if _fold_accents(key) == folded:
            return scale
    return None


def _restore_number_accents(text: str) -> str:
    for unaccented, canonical in _UNACCENTED_NUMBER_FORMS.items():
        text = re.sub(rf"\b{unaccented}\b", canonical, text, flags=re.IGNORECASE)
    return text


def _normalize_mixed_numbers(text: str) -> str:
    """Expand ``25 mil`` → ``25000`` so alpha2digit does not glue digits to ``mil``."""

    def replace(match: re.Match[str]) -> str:
        n = int(match.group(1))
        scale = _multiplier_scale(match.group(2))
        if scale is None:
            return match.group(0)
        return str(n * scale)

    return _RE_MIXED_NUMBER.sub(replace, text)


def _singular_spoken_unit(trailing_word: str) -> str:
    t = trailing_word.lower()
    if t == "euros":
        return "euro"
    if t == "dolares":
        return "dolar"
    if t == "libras":
        return "libra"
    if t == "reais":
        return "real"
    if t == "centavos":
        return "centavo"
    if t == "ienes":
        return "iene"
    return trailing_word


def _normalize_currency_symbols(
    text: str,
    currency_symbol_to_word: dict[str, str] | None,
) -> str:
    if not currency_symbol_to_word:
        return text
    num = r"\d+(?:[.,]\d+)?"
    # Longer symbols (e.g. R$) before $ so both match correctly.
    for symbol, trailing in sorted(
        currency_symbol_to_word.items(), key=lambda item: len(item[0]), reverse=True
    ):
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


class PortugueseNumberNormalizer:
    """Convert Portuguese spelled-out numbers to digits via text2num.alpha2digit."""

    def __init__(self, currency_symbol_to_word: dict[str, str] | None = None) -> None:
        self._currency_symbol_to_word = currency_symbol_to_word
        self._currency_plural_fixes = _currency_plural_fix_patterns(
            currency_symbol_to_word,
        )

    def __call__(self, text: str) -> str:
        text = _normalize_currency_symbols(text, self._currency_symbol_to_word)
        text = _restore_number_accents(text)
        text = _normalize_mixed_numbers(text)
        text = alpha2digit(text, "pt")
        text = _apply_currency_plural_fixes(text, self._currency_plural_fixes)
        return text
