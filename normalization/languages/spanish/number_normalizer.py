"""Convert common Spanish spelled-out numbers to digits (STT-oriented).

Covers 0–999, ``mil`` compounds, and informal ``veinte tres`` → ``23``.
Accepts spellings with or without accents (common in transcripts).
"""

from __future__ import annotations

import unicodedata


def _fold(s: str) -> str:
    s = s.lower()
    return "".join(
        c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn"
    )


def _get(table: dict[str, int], word: str) -> int | None:
    fw = _fold(word)
    for k, v in table.items():
        if _fold(k) == fw:
            return v
    return None


_ONES_1_9: dict[str, int] = {
    "uno": 1,
    "dos": 2,
    "tres": 3,
    "cuatro": 4,
    "cinco": 5,
    "seis": 6,
    "siete": 7,
    "ocho": 8,
    "nueve": 9,
}

_TEENS: dict[str, int] = {
    "diez": 10,
    "once": 11,
    "doce": 12,
    "trece": 13,
    "catorce": 14,
    "quince": 15,
    "dieciseis": 16,
    "diecisiete": 17,
    "dieciocho": 18,
    "diecinueve": 19,
}

_VEINTI: dict[str, int] = {
    "veintiuno": 21,
    "veintidos": 22,
    "veintitres": 23,
    "veinticuatro": 24,
    "veinticinco": 25,
    "veintiseis": 26,
    "veintisiete": 27,
    "veintiocho": 28,
    "veintinueve": 29,
}

_TENS: dict[str, int] = {
    "treinta": 30,
    "cuarenta": 40,
    "cincuenta": 50,
    "sesenta": 60,
    "setenta": 70,
    "ochenta": 80,
    "noventa": 90,
}

_HUNDREDS: dict[str, int] = {
    "cien": 100,
    "ciento": 100,
    "doscientos": 200,
    "trescientos": 300,
    "cuatrocientos": 400,
    "quinientos": 500,
    "seiscientos": 600,
    "setecientos": 700,
    "ochocientos": 800,
    "novecientos": 900,
}


class SpanishNumberNormalizer:
    def __call__(self, text: str) -> str:
        if not text.strip():
            return text
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
        return " ".join(out)

    def _parse_number(self, words: list[str], i: int, n: int) -> tuple[int, int] | None:
        """If words[i:] start with a spelled number, return (exclusive_end_index, value)."""
        if i >= n:
            return None

        fw = _fold(words[i])

        if fw == "cero":
            return i + 1, 0

        # --- Optional leading hundred block (cien/ciento/ doscientos …) ---
        h = _get(_HUNDREDS, words[i])
        if h is not None:
            j = i + 1
            if j < n and _fold(words[j]) == "mil":
                base = h * 1000
                j += 1
                tail = self._parse_number(words, j, n)
                if tail is not None:
                    end, v2 = tail
                    return end, base + v2
                return j, base
            if h == 100:
                sub = self._parse_0_99(words, j, n)
                if sub is not None:
                    je, v = sub
                    return je, 100 + v
                return j, 100
            sub = self._parse_0_99(words, j, n)
            if sub is not None:
                je, v = sub
                return je, h + v
            return j, h

        # --- 0–99 or leading multiplier for "mil" ---
        sub99 = self._parse_0_99(words, i, n)
        if sub99 is None:
            return None
        j, v = sub99
        if j < n and _fold(words[j]) == "mil":
            j += 1
            if j >= n:
                return j, v * 1000
            tail = self._parse_number(words, j, n)
            if tail is not None:
                end, v2 = tail
                return end, v * 1000 + v2
            return j, v * 1000
        return j, v

    def _parse_0_99(self, words: list[str], i: int, n: int) -> tuple[int, int] | None:
        if i >= n:
            return None
        w = words[i]
        fw = _fold(w)

        if fw == "veinte":
            if i + 1 < n:
                o = _get(_ONES_1_9, words[i + 1])
                if o is not None:
                    return i + 2, 20 + o
            return i + 1, 20

        v = _get(_VEINTI, w)
        if v is not None:
            return i + 1, v

        v = _get(_TEENS, w)
        if v is not None:
            return i + 1, v

        v = _get(_ONES_1_9, w)
        if v is not None:
            return i + 1, v

        tens = _get(_TENS, w)
        if tens is None:
            return None
        j = i + 1
        if j < n and _fold(words[j]) == "y":
            j += 1
        if j < n:
            o = _get(_ONES_1_9, words[j])
            if o is not None:
                return j + 1, tens + o
        if i + 1 < n and tens >= 30:
            o = _get(_ONES_1_9, words[i + 1])
            if o is not None:
                return i + 2, tens + o
        return i + 1, tens
