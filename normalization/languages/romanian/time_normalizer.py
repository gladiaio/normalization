"""Romanian spoken and dotted clock times to H:MM.

Romanian says times with words, usually after ``la``, ``ora``, ``e``/``este`` or ``după``:

- ``la opt și jumătate``, ``la opt jumate`` → ``la 8:30``
- ``la opt și un sfert``, ``la opt și-un sfert`` → ``la 8:15``
- ``la opt fără un sfert`` → ``la 7:45``; ``la opt fără zece`` → ``la 7:50``
- ``la ora opt și zece`` → ``la ora 8:10``; ``la șapte patruzeci și cinci`` → ``la 7:45``
- ``la ora 8.30`` (written with a dot) → ``la ora 8:30``

This runs before the time-colon protection, so the result is kept exactly like a written
``8:30``. Only phrases right after a cue are read as times; plain minute numbers (``opt
zece``, ``opt și zece``) only after ``la``/``ora``, and after ``și`` only round minutes
(``opt și zece``) unless the cue is ``ora`` (``la ora opt și cincisprezece``), so quantities
such as ``trei și jumătate`` are left to the number normalizer (``3,5``). A phrase followed by
an amount is a quantity too, whatever its cue: ``la trei și jumătate la sută`` (3,5 %), ``e
doi și un sfert la sută``, ``la doi și jumătate milioane``, ``la zece douăzeci de lei``, ``de
la trei și jumătate la cinci la sută``, ``la 8.30 lei``, and so is one after a verb of
change, where news leaves the unit out (``inflația a crescut la trei și jumătate``, ``a scăzut
de la patru la trei și jumătate``). A dotted date (``până la 15.03.2024``) is not a time. Whether ``opt și jumătate`` means 8:30 or 20:30 cannot be told
from the words; it becomes 8:30.
"""

from __future__ import annotations

import re
from collections.abc import Sequence

from normalization.languages.romanian.number_normalizer import RomanianNumberNormalizer

_CUES = {"la", "ora", "e", "este", "după", "dupa"}
_MINUTE_CUES = {"la", "ora"}
_AND = {"și", "si"}
_WITHOUT = {"fără", "fara"}
_HALF = {"jumătate", "jumatate", "jumate"}
_QUARTER = "sfert"
_AND_A = {"și-un", "si-un"}
_ROUND_MINUTES = {5, 10, 20, 25}
# Words after which a time-like phrase is an amount ("la trei și jumătate la sută" is 3,5 %).
_AMOUNT_AFTER = {
    "procent",
    "procente",
    "mie",
    "mii",
    "milion",
    "milioane",
    "miliard",
    "miliarde",
    "leu",
    "lei",
    "bani",
    "ron",
    "euro",
    "dolar",
    "dolari",
    "lire",
    "kg",
    "kil",
    "kile",
    "kilogram",
    "kilograme",
    "km",
    "kilometru",
    "kilometri",
    "metru",
    "metri",
    "litru",
    "litri",
    "grad",
    "grade",
}
_PERCENT = {"sută", "suta"}
# After these a "la" phrase is the new value of something, not a time: "a crescut la trei și
# jumătate" (3,5). Not "ajuns": "a ajuns la opt și jumătate" is an arrival.
_CHANGE = {
    "crescut",
    "crește",
    "creste",
    "scăzut",
    "scazut",
    "scade",
    "urcat",
    "urcă",
    "urca",
    "coborât",
    "coborat",
    "coboară",
    "coboara",
    "redus",
    "majorat",
    "mărit",
    "marit",
    "diminuat",
    "avansat",
}
# Words skipped when looking back from a "la" for that verb: "a scăzut de la patru la".
_BETWEEN = {"de", "la", "până", "pana"}
_SYMBOLS = ("%", "€", "$", "£", "°")

_TOKEN = re.compile(r"(\S+)")
_EDGE = re.compile(r"^([^\w]*)(.*?)([^\w-]*)$", re.UNICODE)
# Not a date: "15.03.2024" continues past the minutes.
_DOTTED = re.compile(r"\b(la|ora)\s+(\d{1,2})\.([0-5]\d)\b(?![.,]\d)", re.IGNORECASE)
_CEDILLA = str.maketrans("şţŞŢ", "șțȘȚ")


def _split(text: str) -> tuple[list[str], list[tuple[str, ...]], list[str]]:
    """Tokens, their (lead, core, trail) parts, and the casefolded cores."""
    tokens = _TOKEN.findall(text)
    parts = [_EDGE.match(token).groups() for token in tokens]  # type: ignore[union-attr]
    words = [core.translate(_CEDILLA).casefold() for _, core, _ in parts]
    return tokens, parts, words


class RomanianTimeNormalizer:
    def __init__(self) -> None:
        self._numbers = RomanianNumberNormalizer()

    def __call__(self, text: str) -> str:
        text = _DOTTED.sub(self._dotted, text)
        tokens, parts, words = _split(text)
        output: list[str] = []
        i = 0
        while i < len(tokens):
            output.append(tokens[i])
            if (
                words[i] in _CUES
                and not parts[i][2]
                and i + 1 < len(tokens)
                and not self._after_change(words, parts, i)
            ):
                end = i + 1
                while (
                    end < len(tokens)
                    and not parts[end][0]
                    and (end == i + 1 or not parts[end - 1][2])
                ):
                    end += 1
                found = self._time(words[i + 1 : end], words[i])
                if found and not self._amount_follows(words, parts, i + found[2]):
                    hour, minute, used = found
                    output.append(f"{hour}:{minute:02d}{parts[i + used][2]}")
                    i += used + 1
                    continue
            i += 1
        return " ".join(output)

    def _after_change(
        self, words: list[str], parts: Sequence[tuple[str, ...]], cue: int
    ) -> bool:
        """Whether the ``la`` at ``cue`` follows a verb of change, over ``de``/``la``/``până``
        and the numbers of a range ("a scăzut de la patru la trei și jumătate")."""
        if words[cue] != "la":
            return False
        k = cue - 1
        while (
            k >= 0
            and not parts[k][2]
            and (
                words[k] in _BETWEEN
                or words[k].isdigit()
                or self._numbers.parse([words[k]])
            )
        ):
            k -= 1
        return k >= 0 and not parts[k][2] and words[k] in _CHANGE

    def _dotted(self, match: re.Match[str]) -> str:
        if int(match.group(2)) > 24:
            return match.group(0)
        _, parts, words = _split(match.string[match.end() :])
        if self._amount_after(words, parts, 0, first_lead=True):
            return match.group(0)  # "la 8.30 lei"
        return f"{match.group(1)} {int(match.group(2))}:{match.group(3)}"

    def _amount_follows(
        self, words: list[str], parts: Sequence[tuple[str, ...]], last: int
    ) -> bool:
        """Whether what follows the phrase ending at token ``last`` makes it an amount."""
        if any(symbol in parts[last][2] for symbol in _SYMBOLS):
            return True
        if parts[last][2]:
            return False  # punctuation ends the phrase
        return self._amount_after(words, parts, last + 1)

    def _amount_after(
        self,
        words: list[str],
        parts: Sequence[tuple[str, ...]],
        start: int,
        first_lead: bool = False,
        depth: int = 0,
    ) -> bool:
        """Whether the tokens from ``start`` on are an amount's unit: "lei", "de lei", "la
        sută", "%", or another amount with one ("la cinci la sută", in a range)."""
        if start >= len(words):
            return False
        lead = parts[start][0]
        if lead:
            # A symbol right after the time-like phrase, or after a dotted one ("8.30 €").
            return lead.startswith(_SYMBOLS) and (first_lead or not parts[start][1])
        word = words[start]
        if word in _AMOUNT_AFTER:
            return True
        joined = (
            start + 1 < len(words) and not parts[start][2] and not parts[start + 1][0]
        )
        following = words[start + 1] if joined else None
        if word == "de":
            return following in _AMOUNT_AFTER
        if word != "la" or following is None:
            return False
        if following in _PERCENT:
            return True
        parsed = self._number(words[start + 1 :])
        if depth or not parsed or parts[start + parsed[1]][2]:
            return False
        return self._amount_after(words, parts, start + 1 + parsed[1], depth=depth + 1)

    def _number(self, words: list[str]) -> tuple[int, int] | None:
        if words and words[0].isdigit():
            return int(words[0]), 1
        return self._numbers.parse(words)

    def _time(self, words: list[str], cue: str) -> tuple[int, int, int] | None:
        """(hour, minute, words used) for a time phrase after ``cue`` at the start of ``words``."""
        parsed = self._number(words)
        if parsed is None or not 0 <= parsed[0] <= 24:
            return None
        hour, j = parsed
        rest = words[j:]

        def at(k: int) -> str:
            return rest[k] if k < len(rest) else ""

        if at(0) in _HALF:
            return hour, 30, j + 1
        if at(0) in _AND and at(1) in _HALF:
            return hour, 30, j + 2
        if at(0) in _AND_A and at(1) == _QUARTER:
            return hour, 15, j + 2
        if at(0) in _AND and at(1) == _QUARTER:
            return hour, 15, j + 2
        if at(0) in _AND and at(1) == "un" and at(2) == _QUARTER:
            return hour, 15, j + 3
        if at(0) in _WITHOUT:
            before = (hour - 1) % 24 or (12 if hour == 1 else 0)
            if at(1) == "un" and at(2) == _QUARTER:
                return before, 45, j + 3
            if at(1) == _QUARTER:
                return before, 45, j + 2
            minutes = self._number(rest[1:])
            if minutes and minutes[0] in _ROUND_MINUTES:
                return before, 60 - minutes[0], j + 1 + minutes[1]
            return None
        if cue not in _MINUTE_CUES:
            return None
        if at(0) in _AND:
            minutes = self._number(rest[1:])
            if minutes and (
                minutes[0] in _ROUND_MINUTES or (cue == "ora" and 1 <= minutes[0] <= 59)
            ):
                return hour, minutes[0], j + 1 + minutes[1]
            return None
        minutes = self._number(rest)
        if minutes and 10 <= minutes[0] <= 59 and not rest[0].isdigit():
            return hour, minutes[0], j + minutes[1]
        return None
