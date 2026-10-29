"""Romanian number normalizer (STT-oriented).

``text2num.alpha2digit`` does not support Romanian, so this module parses spelled-out
cardinals for the patterns found in transcripts:

- units, teens and tens, including the informal contracted teens of everyday speech
  (``cincișpe`` = 15, ``unșpe`` = 11, ``doișpe``/``douășpe`` = 12), their most reduced
  forms (``cinșpe``), colloquial tens (``douăj`` = 20) and fused tens-and-five
  (``patrușcinci`` = 45);
- ``X zeci și Y`` compounds (``douăzeci și cinci`` = 25), also written as one word
  (``douăzecișicinci``);
- hundreds (``trei sute``), and the multipliers ``mie``/``mii``, ``milion``/``milioane``,
  ``miliard``/``miliarde``, with the ``de`` Romanian puts between a number from 20 up and
  its multiplier (``douăzeci de mii`` = 20000);
- ``un``/``o`` count as 1 only before ``sută``/``mie``/``milion``/``miliard``, so articles
  (``o zi``, ``un om``) stay words;
- ordinals after ``al``/``a`` (``al treilea`` = ``al 3``, ``a opta``, ``al douăzeci și
  cincilea``) and digit ordinals (``al 3-lea``, ``a 3-a`` → ``al 3``, ``a 3``), and ``întâi``
  before a month (``întâi decembrie`` = ``1 decembrie``).

A half after an amount is its decimal: ``trei kile jumate``, ``trei kilograme și jumătate
(de mere)`` and ``trei și jumătate`` become ``3 virgula 5`` (with the noun after it), like
``3,5``; a quarter likewise (``doi și un sfert la sută``, ``două ore și un sfert`` → ``2
virgula 25``, like ``2,25``). ``un``/``o`` count as 1 before a measure, whose decimal takes the
plural as written (``o oră și jumătate`` = ``1,5 ore``), and a half after a multiplier is a
decimal of it (``două milioane și jumătate`` = ``2,5 milioane``). Clock times (``la opt și
jumătate``) are read earlier, by the time normalizer.

Currency symbols before or after an amount become the currency word after it (``1.200 €``
and ``€1.200`` → ``1200 euro``), as Romanian says it (``o mie două sute de euro``), once the
spelled numbers are digits. A symbol after an amount is read first, since that is where
Romanian writes it (``5 € 2 kilograme`` and ``cinci € 2 kilograme`` → ``5 euro 2``), but not
one that already has its amount after it (``€50 €100``); ``20 de €`` is ``20 euro``.

A number phrase never runs across punctuation, and a unit directly after a unit starts a new
number (``doi trei`` → ``2 3``). Words are matched with and without diacritics, and the
legacy cedilla letters ş/ţ are rewritten as ș/ț.

Romanian puts ``de`` between a number and its noun when the number is at least 20 or ends in
00 (``douăzeci de grade``, ``o sută de lei``, but ``cinci grade``). Written forms such as
``20°`` or ``20 grade`` have no ``de``, so that grammatical ``de`` is dropped after such
numbers: ``20°``, ``20 de grade`` and ``douăzeci de grade`` all become ``20 grade``. A ``de``
after other numbers, or starting a preposition or a discourse marker (``de la`` "from",
``douăzeci de pe listă``, ``în 2024 de exemplu``), stays.
"""

from __future__ import annotations

import re

from normalization.constants import ProtectPlaceholder

_UNITS: dict[str, int] = {
    "zero": 0,
    "unu": 1,
    "una": 1,
    "doi": 2,
    "două": 2,
    "doua": 2,
    "trei": 3,
    "patru": 4,
    "cinci": 5,
    "șase": 6,
    "sase": 6,
    "șapte": 7,
    "sapte": 7,
    "opt": 8,
    "nouă": 9,
    "noua": 9,
}

_TEENS: dict[str, int] = {
    "zece": 10,
    "unsprezece": 11,
    "unșpe": 11,
    "unspe": 11,
    "doisprezece": 12,
    "douăsprezece": 12,
    "douasprezece": 12,
    "doișpe": 12,
    "doispe": 12,
    "douășpe": 12,  # feminine, as in "e ora douășpe"
    "douaspe": 12,
    "doușpe": 12,
    "douspe": 12,
    "treisprezece": 13,
    "treișpe": 13,
    "treispe": 13,
    "paisprezece": 14,
    "paișpe": 14,
    "paispe": 14,
    "cincisprezece": 15,
    "cincișpe": 15,
    "cincispe": 15,
    "cinșpe": 15,
    "cinspe": 15,
    "șaisprezece": 16,
    "saisprezece": 16,
    "șaișpe": 16,
    "saispe": 16,
    "șaptesprezece": 17,
    "saptesprezece": 17,
    "șaptișpe": 17,
    "saptispe": 17,
    "optsprezece": 18,
    "optișpe": 18,
    "optispe": 18,
    "nouăsprezece": 19,
    "nouasprezece": 19,
    "nouășpe": 19,
    "nouaspe": 19,
}

_TENS: dict[str, int] = {
    "douăzeci": 20,
    "douazeci": 20,
    "douăj": 20,  # colloquial
    "douaj": 20,
    "treizeci": 30,
    "treij": 30,
    "patruzeci": 40,
    "patruj": 40,
    "cincizeci": 50,
    "cinzeci": 50,
    "șaizeci": 60,
    "saizeci": 60,
    "șaptezeci": 70,
    "saptezeci": 70,
    "optzeci": 80,
    "nouăzeci": 90,
    "nouazeci": 90,
}

# Tens and "cinci" fused in fast speech (patrușcinci = patruzeci și cinci): complete numbers.
_FUSED: dict[str, int] = {
    "douășcinci": 25,
    "douascinci": 25,
    "treișcinci": 35,
    "treiscinci": 35,
    "patrușcinci": 45,
    "patruscinci": 45,
}

_HUNDRED: dict[str, int] = {"sută": 100, "suta": 100, "sute": 100}

_LARGE: dict[str, int] = {
    "mie": 1_000,
    "mii": 1_000,
    "milion": 1_000_000,
    "milioane": 1_000_000,
    "miliard": 1_000_000_000,
    "miliarde": 1_000_000_000,
}

_ARTICLES = {"un", "o"}

_ORDINALS: dict[str, str] = {
    "doilea": "2",
    "treilea": "3",
    "patrulea": "4",
    "cincilea": "5",
    "șaselea": "6",
    "saselea": "6",
    "șaptelea": "7",
    "saptelea": "7",
    "optulea": "8",
    "nouălea": "9",
    "noualea": "9",
    "zecelea": "10",
    "treia": "3",
    "patra": "4",
    "cincea": "5",
    "șasea": "6",
    "sasea": "6",
    "șaptea": "7",
    "saptea": "7",
    "zecea": "10",
}

NUMBER_WORDS: list[str] = [*_UNITS, *_TEENS, *_FUSED, *_TENS, *_HUNDRED, *_LARGE]
"""Every cardinal word the normalizer understands (for ``LanguageConfig.number_words``)."""

_TOKEN = re.compile(r"(\S+)")
_EDGE = re.compile(r"^([^\w]*)(.*?)([^\w]*)$", re.UNICODE)
_DIGIT_ORDINAL = re.compile(r"\b(\d+)-(?:lea|a)\b", re.IGNORECASE)
_CEDILLA = str.maketrans("şţŞŢ", "șțȘȚ")
# Decimals are protected (12,50 → 12XDECIMALX50) before this runs.
_AMOUNT = rf"\d+(?:(?:[.,]|{ProtectPlaceholder.DECIMAL_SEPARATOR.value})\d+)*"
_AND = r"(?:și|si)"
_HALF = r"(?:jumătate|jumatate|jumate)"
_QUARTER = rf"(?:{_AND} (?:un )?|{_AND}-un )sfert"
# Nouns a colloquial half follows without "și" ("trei kile jumate", "un an jumate"), and the
# only nouns before which "un"/"o" count as 1 in a half or quarter ("o oră și jumătate").
_MEASURES = {
    "kil", "kile", "kilogram", "kilograme", "kg", "gram", "grame", "litru", "litri",
    "metru", "metri", "km", "kilometru", "kilometri", "oră", "ora", "ore", "minut", "minute",
    "zi", "zile", "săptămână", "saptamana", "săptămâni", "saptamani", "lună", "luna", "luni",
    "an", "ani", "leu", "lei", "euro", "dolar", "dolari",
}  # fmt: skip
# Romanian puts a decimal amount's noun in the plural ("1,5 ore", "1,5 kilograme").
_PLURAL_MEASURES = {
    "oră": "ore", "ora": "ore", "kilogram": "kilograme", "gram": "grame", "litru": "litri",
    "metru": "metri", "kilometru": "kilometri", "minut": "minute", "zi": "zile",
    "săptămână": "săptămâni", "saptamana": "saptamani", "lună": "luni", "luna": "luni",
    "an": "ani", "leu": "lei", "dolar": "dolari",
}  # fmt: skip
_MEASURE = "|".join(sorted((re.escape(m) for m in _MEASURES), key=lambda m: -len(m)))
# A half or quarter after an amount, or after an amount and its noun: "trei și jumătate", "opt
# ore și jumătate", "trei kilograme și jumătate de mere", "o oră și un sfert". The trailing
# "de" is captured: without a noun, "trei și jumătate de pâine" is not 3,5.
_HALVES = re.compile(
    rf"\b(\d+|un|o) (?:(?!{_AND}\b)([^\W\d_]+) )?{_AND} {_HALF}\b( de\b)?",
    re.IGNORECASE,
)
_QUARTERS = re.compile(
    rf"\b(\d+|un|o) (?:(?!{_AND}\b)([^\W\d_]+) )?{_QUARTER}\b( de\b)?", re.IGNORECASE
)
_COLLOQUIAL_HALVES = re.compile(rf"\b(\d+|un|o) ({_MEASURE}) {_HALF}\b", re.IGNORECASE)
# A half or quarter after a multiplier is a decimal of it, as written: "două milioane și
# jumătate" is "2,5 milioane", not 2000000,5.
_PLURAL_MULTIPLIER = {
    "mie": "mii",
    "mii": "mii",
    "milion": "milioane",
    "milioane": "milioane",
    "miliard": "miliarde",
    "miliarde": "miliarde",
}
_MONTHS = {
    "ianuarie", "februarie", "martie", "aprilie", "mai", "iunie", "iulie", "august",
    "septembrie", "octombrie", "noiembrie", "decembrie",
}  # fmt: skip
# A "de" before these is not the one linking a number to its noun: "în 2024 de exemplu",
# "douăzeci de pe listă", "de la" ("from").
_NOT_LINKING = {
    "la", "pe", "sub", "către", "catre", "lângă", "langa", "după", "dupa", "exemplu",
    "fapt", "asemenea", "obicei", "ce", "când", "cand",
}  # fmt: skip


def _alternation(words: dict[str, int]) -> str:
    """Regex alternation of the words, longest first."""
    ordered: list[str] = sorted(words.keys(), key=lambda word: -len(word))
    return "|".join(ordered)


_GLUED = re.compile(
    rf"\b({_alternation(_TENS)})(și|si)({_alternation(_UNITS)})\b", re.IGNORECASE
)


def _fold(word: str) -> str:
    return word.translate(_CEDILLA).casefold()


def _ordinal_stems(word: str) -> list[str]:
    """Cardinal forms an ordinal word may be built on: unsprezecelea, douăzecea, cincea."""
    stems = []
    if word.endswith("ulea"):
        stems.append(word[:-4])  # optulea
    if word.endswith("lea"):
        stems.append(word[:-3])  # unsprezecelea, douăzecilea, nouălea
    if word.endswith("ea"):
        stems += [word[:-2] + "e", word[:-2] + "i"]  # unsprezecea, douăzecea, cincea
    if word.endswith("a"):
        stems.append(word[:-1])  # opta
    return stems


class RomanianNumberNormalizer:
    """Replace spelled-out Romanian numbers with digits, keeping surrounding punctuation."""

    def __init__(
        self,
        currency_symbol_to_word: dict[str, str] | None = None,
        decimal_word: str = "virgula",
    ) -> None:
        self._decimal = decimal_word
        self._currency: list[tuple[re.Pattern[str], re.Pattern[str], str]] = []
        for symbol, word in (currency_symbol_to_word or {}).items():
            sym = re.escape(symbol)
            self._currency.append(
                (
                    re.compile(rf"{sym}\s*({_AMOUNT})"),
                    # Not an amount that has the symbol before it ("€50 €100"), nor the
                    # tail of a longer number; "20 de €" is "20 euro", like "20 de euro".
                    re.compile(
                        rf"(?<![\d.,])(?<!{sym})(?<!{sym} )({_AMOUNT})\s*(?:de\s+)?{sym}"
                    ),
                    word,
                )
            )

    def __call__(self, text: str) -> str:
        text = _GLUED.sub(r"\1 \2 \3", text.translate(_CEDILLA))
        text = _DIGIT_ORDINAL.sub(r"\1", text)
        tokens = _TOKEN.findall(text)
        if not tokens:
            return text
        parts = [_EDGE.match(token).groups() for token in tokens]  # type: ignore[union-attr]
        cores = [_fold(core) for _, core, _ in parts]
        output: list[str] = []
        i = 0
        while i < len(tokens):
            lead, _, trail = parts[i]
            # A number phrase may not run across punctuation between its words.
            limit = i + 1
            while (
                limit < len(tokens) and not parts[limit - 1][2] and not parts[limit][0]
            ):
                limit += 1
            if i > 0 and cores[i - 1] in ("al", "a") and not parts[i - 1][2]:
                ordinal = self._ordinal(cores[i:limit])
                if ordinal:
                    value, length = ordinal
                    output.append(f"{lead}{value}{parts[i + length - 1][2]}")
                    i += length
                    continue
            if (
                cores[i] in ("întâi", "intai")
                and i + 1 < limit
                and cores[i + 1] in _MONTHS
            ):
                output.append(f"{lead}1{trail}")  # "întâi decembrie" = "1 decembrie"
                i += 1
                continue
            parsed = self._parse(cores[i:limit])
            if parsed:
                value, length = parsed
                fraction = self._multiplier_fraction(cores[i:limit], value, length)
                if fraction:
                    written, length = fraction
                    output.append(f"{lead}{written}{parts[i + length - 1][2]}")
                else:
                    output.append(f"{lead}{value}{parts[i + length - 1][2]}")
                i += length
            else:
                output.append(tokens[i])
                i += 1
        text = " ".join(self._drop_linking_de(output))
        # Currency after the numbers are digits, a symbol after its amount first, as Romanian
        # writes it: "cinci € 2 kilograme" and "5 € 2 kilograme" are "5 euro 2 kilograme".
        for before, after, word in self._currency:
            text = after.sub(rf"\1 {word}", text)
            text = before.sub(rf"\1 {word}", text)
        text = _COLLOQUIAL_HALVES.sub(self._colloquial_half, text)
        text = _HALVES.sub(lambda m: self._fraction(m, "5"), text)
        return _QUARTERS.sub(lambda m: self._fraction(m, "25"), text)

    def _fraction(self, match: re.Match[str], digits: str) -> str:
        """``N [noun] și jumătate/un sfert`` as ``N virgula 5/25 [noun]``."""
        number, noun, de = match.group(1), match.group(2), match.group(3) or ""
        if number.casefold() in _ARTICLES:
            if noun is None or noun.casefold() not in _MEASURES:
                return match.group(0)
            number = "1"
        if noun is None and de:
            return match.group(0)  # "trei și jumătate de pâine"
        noun_text = f" {_PLURAL_MEASURES.get(_fold(noun), noun)}" if noun else ""
        return f"{number} {self._decimal} {digits}{noun_text}{de}"

    def _colloquial_half(self, match: re.Match[str]) -> str:
        number = "1" if match.group(1).casefold() in _ARTICLES else match.group(1)
        noun = _PLURAL_MEASURES.get(_fold(match.group(2)), match.group(2))
        return f"{number} {self._decimal} 5 {noun}"

    def _multiplier_fraction(
        self, words: list[str], value: int, length: int
    ) -> tuple[str, int] | None:
        """("N virgula 5 milioane", words used) for ``N milioane și jumătate`` and quarters."""
        multiplier = words[length - 1]
        if multiplier not in _PLURAL_MULTIPLIER or value % _LARGE[multiplier]:
            return None
        count = value // _LARGE[multiplier]
        if not 0 < count < 1000:
            return None
        conjunction, second, third = [*words[length : length + 3], "", "", ""][:3]
        if conjunction in ("și-un", "si-un") and second == "sfert":
            digits, extra = "25", 2
        elif conjunction in ("și", "si") and second == "un" and third == "sfert":
            digits, extra = "25", 3
        elif conjunction in ("și", "si") and second in (
            "jumătate",
            "jumatate",
            "jumate",
        ):
            digits, extra = "5", 2
        else:
            return None
        plural = _PLURAL_MULTIPLIER[multiplier]
        return f"{count} {self._decimal} {digits} {plural}", length + extra

    def _ordinal(self, words: list[str]) -> tuple[str, int] | None:
        """(digits, words used) for an ordinal after "al"/"a": treilea, opta, douăzecilea."""
        if words and words[0] in _ORDINALS:
            return _ORDINALS[words[0]], 1
        for length in range(1, min(len(words), 5) + 1):
            for stem in _ordinal_stems(words[length - 1]):
                parsed = self._parse([*words[: length - 1], stem])
                if parsed and parsed[1] == length:
                    return str(parsed[0]), length
        return None

    def parse(self, words: list[str]) -> tuple[int, int] | None:
        """(value, words used) for the number phrase at the start of casefolded ``words``."""
        return self._parse(words)

    @staticmethod
    def _drop_linking_de(tokens: list[str]) -> list[str]:
        """Drop the ``de`` that links a number of at least 20 (or ending in 00) to its noun."""
        out: list[str] = []
        for i, token in enumerate(tokens):
            if (
                token.casefold() == "de"
                and 0 < i < len(tokens) - 1
                and out
                and out[-1].isdigit()
                and (int(out[-1]) % 100 == 0 or int(out[-1]) % 100 >= 20)
                and tokens[i + 1][:1].isalpha()
                and _fold(_EDGE.match(tokens[i + 1]).group(2)) not in _NOT_LINKING  # type: ignore[union-attr]
            ):
                continue
            out.append(token)
        return out

    @staticmethod
    def _kind(word: str, following: str | None) -> tuple[str, int] | None:
        if word in _UNITS:
            return "unit", _UNITS[word]
        if word in _TEENS:
            return "teen", _TEENS[word]
        if word in _FUSED:
            return "teen", _FUSED[word]
        if word in _TENS:
            return "ten", _TENS[word]
        if word in _HUNDRED:
            return "hundred", 100
        if word in _LARGE:
            return "large", _LARGE[word]
        if word in _ARTICLES and following in (*_HUNDRED, *_LARGE):
            return "unit", 1
        return None

    def _parse(self, words: list[str]) -> tuple[int, int] | None:
        """Longest well-formed number phrase at the start of ``words``: (value, words used).

        Grammar: ``[unit sute] [ten [și unit] | teen | unit]`` with the large multipliers,
        ``de`` before a multiplier from 20 up, and ``o``/``un`` as 1 only before a hundred or a
        multiplier.
        """
        total = current = 0
        previous: str | None = None
        used = i = 0
        while i < len(words):
            word = words[i]
            following = words[i + 1] if i + 1 < len(words) else None
            if word in ("și", "si"):
                if (
                    previous == "ten"
                    and following is not None
                    and _UNITS.get(following, 0) > 0
                ):
                    previous, i = "și", i + 1
                    continue
                break
            if word == "de":
                if current >= 20 and following in _LARGE:
                    i += 1
                    continue
                break
            kind = self._kind(word, following)
            if kind is None:
                break
            name, number = kind
            after = (
                (None, "și", "hundred", "large")
                if name == "unit"
                else (None, "hundred", "large")
            )
            if name in ("unit", "teen", "ten") and previous in after:
                current += number
            elif name == "hundred" and previous == "unit" and 0 < current < 10:
                current *= 100
            elif name == "large" and previous not in (None, "large") and current > 0:
                total, current = total + current * number, 0
            else:
                break
            previous, i = name, i + 1
            used = i
        return (total + current, used) if used else None
