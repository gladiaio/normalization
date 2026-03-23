import re
from fractions import Fraction
from typing import Iterator, Match

"""
Dutch number normalizer: spelled-out numbers to digits.

- Dutch compound order: ones + "en" + tens (e.g. "een en twintig" -> 21).
- Vocabulary: nul, een, twee, ..., tien, elf, twaalf, ..., twintig, dertig, ...
- Multipliers: honderd, duizend, miljoen, miljard, biljoen.
- Handles currency (euro, dollar, pond, cent), percent (procent), and decimal (komma).
- Currency output follows Dutch word order: amount then unit (e.g. €10 and "tien euro" -> "10 euros").
"""


class DutchNumberNormalizer:
    def __init__(self, currency_symbol_to_word: dict[str, str] | None = None):
        self.zeros = {"nul"}
        self.ones: dict[str, int] = {
            name: i
            for i, name in enumerate(
                [
                    "een",
                    "twee",
                    "drie",
                    "vier",
                    "vijf",
                    "zes",
                    "zeven",
                    "acht",
                    "negen",
                    "tien",
                    "elf",
                    "twaalf",
                    "dertien",
                    "veertien",
                    "vijftien",
                    "zestien",
                    "zeventien",
                    "achttien",
                    "negentien",
                ],
                start=1,
            )
        }
        self.ones_plural = {}
        self.ones_ordinal = {
            "eerste": (1, "e"),
            "tweede": (2, "e"),
            "derde": (3, "e"),
            "vierde": (4, "e"),
            "vijfde": (5, "e"),
            "zesde": (6, "e"),
            "zevende": (7, "e"),
            "achtste": (8, "e"),
            "negende": (9, "e"),
            "tiende": (10, "e"),
            **{
                name + "de": (value, "e")
                for name, value in self.ones.items()
                if value > 10 and value < 20
            },
        }
        self.ones_suffixed: dict[str, tuple[int, str]] = {
            **self.ones_plural,
            **self.ones_ordinal,
        }

        self.tens = {
            "twintig": 20,
            "dertig": 30,
            "veertig": 40,
            "vijftig": 50,
            "zestig": 60,
            "zeventig": 70,
            "tachtig": 80,
            "negentig": 90,
        }
        self.tens_plural = {
            name + "en": (value, "en") for name, value in self.tens.items()
        }
        self.tens_ordinal = {
            name + "ste": (value, "e") for name, value in self.tens.items()
        }
        self.tens_suffixed = {**self.tens_plural, **self.tens_ordinal}

        self.multipliers = {
            "honderd": 100,
            "duizend": 1_000,
            "miljoen": 1_000_000,
            "miljard": 1_000_000_000,
            "biljoen": 1_000_000_000_000,
        }
        self.multipliers_plural = {
            name + "en": (value, "en") for name, value in self.multipliers.items()
        }
        self.multipliers_ordinal = {
            name + "ste": (value, "e") for name, value in self.multipliers.items()
        }
        self.multipliers_suffixed = {
            **self.multipliers_plural,
            **self.multipliers_ordinal,
        }
        self.decimals = {*self.ones, *self.tens, *self.zeros}

        self.preceding_prefixers = {
            "min": "-",
            "minus": "-",
            "negatief": "-",
            "plus": "+",
            "positief": "+",
            "nul": "0",
        }
        self.following_prefixers = {
            "pond": "£",
            "ponden": "£",
            "euro": "€",
            "euro's": "€",
            "euros": "€",
            "yen": "¥",
            "yens": "¥",
            "dollar": "$",
            "dollars": "$",
            "cent": "¢",
            "centen": "¢",
            "cents": "¢",
        }
        self.prefixes = set(
            list(self.preceding_prefixers.values())
            + list(self.following_prefixers.values())
        )
        self.suffixers = {
            "procent": "%",
        }
        self.specials = {"en", "dubbel", "drievoudig", "komma"}

        self._currency_trailing = currency_symbol_to_word or {}

        self.words = {
            key
            for mapping in [
                self.zeros,
                self.ones,
                self.ones_suffixed,
                self.tens,
                self.tens_suffixed,
                self.multipliers,
                self.multipliers_suffixed,
                self.preceding_prefixers,
                self.following_prefixers,
                self.suffixers,
                self.specials,
            ]
            for key in mapping
        }
        self.literal_words = {"een"}

    def process_words(self, words: list[str]) -> Iterator[str]:  # noqa: C901
        prefix: str | None = None
        value: str | int | None = None
        pending_ones: int | None = None  # Dutch: "een en twintig" -> 21
        skip = False

        def to_fraction(s: str | float):
            try:
                return Fraction(s)
            except ValueError:
                return None

        def output(result: str | int):
            nonlocal prefix, value, pending_ones
            result = str(result)
            if prefix is not None:
                trailing = self._currency_trailing.get(prefix)
                if trailing is not None:
                    result = f"{result} {trailing}"
                else:
                    result = prefix + result
            value = None
            pending_ones = None
            prefix = None
            return result

        if len(words) == 0:
            return

        for i, current in enumerate(words):
            prev = words[i - 1] if i != 0 else None
            next_word = words[i + 1] if i != len(words) - 1 else None
            if skip:
                skip = False
                continue

            current_lower = current.lower()
            prev_lower = prev.lower() if prev is not None else None
            next_lower = next_word.lower() if next_word is not None else None

            next_is_numeric = next_word is not None and re.match(
                r"^\d+(\.\d+)?$", next_word
            )

            if re.match(r"^\d+$", current):
                if value is not None:
                    yield output(value)
                if pending_ones is not None:
                    yield output(pending_ones)
                yield output(current)
                continue

            has_prefix = current[0] in self.prefixes
            current_without_prefix = current[1:] if has_prefix else current
            if re.match(r"^\d+(\.\d+)?$", current_without_prefix):
                f = to_fraction(current_without_prefix)
                if f is None:
                    raise ValueError("Converting the fraction failed")

                if value is not None:
                    if isinstance(value, str) and value.endswith("."):
                        value = str(value) + str(current)
                        continue
                    else:
                        yield output(value)
                if pending_ones is not None:
                    yield output(pending_ones)

                prefix = current[0] if has_prefix else prefix
                if f.denominator == 1:
                    value = f.numerator
                else:
                    value = current_without_prefix
            elif current_lower not in self.words:
                if value is not None:
                    yield output(value)
                if pending_ones is not None:
                    yield output(pending_ones)
                yield output(current)
            elif current_lower in self.zeros:
                value = str(value or "") + "0"
            elif current_lower in self.ones:
                ones = self.ones[current_lower]

                if (
                    next_lower == "en"
                    and next_word is not None
                    and i + 2 < len(words)
                    and words[i + 2].lower() in self.tens
                ):
                    pending_ones = ones
                    skip = True
                elif value is None and pending_ones is None:
                    value = ones
                elif isinstance(value, str) or prev_lower in self.ones:
                    if prev_lower in self.tens and ones < 10:
                        value = value[:-1] + str(ones)  # type: ignore
                    else:
                        value = str(value) + str(ones)
                elif ones < 10:
                    if value is not None and value % 10 == 0:
                        value += ones
                    else:
                        value = str(value or "") + str(ones)
                else:
                    if value is not None and value % 100 == 0:
                        value += ones
                    else:
                        value = str(value or "") + str(ones)
            elif current_lower in self.ones_suffixed:
                ones, suffix = self.ones_suffixed[current_lower]
                if value is None and pending_ones is None:
                    yield output(str(ones) + suffix)
                elif isinstance(value, str) or prev_lower in self.ones:
                    if prev_lower in self.tens and ones < 10:
                        yield output(value[:-1] + str(ones) + suffix)  # type: ignore
                    else:
                        yield output(str(value) + str(ones) + suffix)
                elif ones < 10 and value is not None:
                    if value % 10 == 0:
                        yield output(str(value + ones) + suffix)
                    else:
                        yield output(str(value) + str(ones) + suffix)
                else:
                    if value is not None and value % 100 == 0:
                        yield output(str(value + ones) + suffix)
                    else:
                        yield output(str(value or "") + str(ones) + suffix)
                value = None
                pending_ones = None
            elif current_lower in self.tens:
                tens = self.tens[current_lower]
                if pending_ones is not None:
                    value = tens + pending_ones
                    pending_ones = None
                elif value is None:
                    value = tens
                elif isinstance(value, str):
                    value = str(value) + str(tens)
                else:
                    if value % 100 == 0:
                        value += tens
                    else:
                        value = str(value) + str(tens)
            elif current_lower in self.tens_suffixed:
                tens, suffix = self.tens_suffixed[current_lower]
                if pending_ones is not None:
                    yield output(str(tens + pending_ones) + suffix)
                    pending_ones = None
                elif value is None:
                    yield output(str(tens) + suffix)
                elif isinstance(value, str):
                    yield output(str(value) + str(tens) + suffix)
                else:
                    if value % 100 == 0:
                        yield output(str(value + tens) + suffix)
                    else:
                        yield output(str(value) + str(tens) + suffix)
                value = None
            elif current_lower in self.multipliers:
                multiplier = self.multipliers[current_lower]
                if pending_ones is not None:
                    yield output(pending_ones)
                    pending_ones = None
                if value is None:
                    value = multiplier
                elif isinstance(value, str) or value == 0:
                    f = to_fraction(value)
                    p = f * multiplier if f is not None else None
                    if p is not None and p.denominator == 1:
                        value = p.numerator
                    else:
                        yield output(value)
                        value = multiplier
                else:
                    before = value // 1000 * 1000
                    residual = value % 1000
                    value = before + residual * multiplier
            elif current_lower in self.multipliers_suffixed:
                multiplier, suffix = self.multipliers_suffixed[current_lower]
                if pending_ones is not None:
                    yield output(pending_ones)
                    pending_ones = None
                if value is None:
                    yield output(str(multiplier) + suffix)
                elif isinstance(value, str):
                    f = to_fraction(value)
                    p = f * multiplier if f is not None else None
                    if p is not None and p.denominator == 1:
                        yield output(str(p.numerator) + suffix)
                    else:
                        yield output(value)
                        yield output(str(multiplier) + suffix)
                else:
                    before = value // 1000 * 1000
                    residual = value % 1000
                    value = before + residual * multiplier
                    yield output(str(value) + suffix)
                value = None
            elif current_lower in self.preceding_prefixers:
                if value is not None:
                    yield output(value)
                if pending_ones is not None:
                    yield output(pending_ones)

                if next_lower in self.words or next_is_numeric:
                    prefix = self.preceding_prefixers[current_lower]
                else:
                    yield output(current)
            elif current_lower in self.following_prefixers:
                if value is not None:
                    prefix = self.following_prefixers[current_lower]
                    yield output(value)
                elif pending_ones is not None:
                    yield output(pending_ones)
                    yield output(current)
                else:
                    yield output(current)
            elif current_lower in self.suffixers:
                if value is not None:
                    suffix = self.suffixers[current_lower]
                    yield output(str(value) + suffix)
                elif pending_ones is not None:
                    yield output(str(pending_ones) + self.suffixers[current_lower])
                else:
                    yield output(current)
                value = None
                pending_ones = None
            elif current_lower in self.specials:
                if next_lower not in self.words and not next_is_numeric:
                    if value is not None:
                        yield output(value)
                    if pending_ones is not None:
                        yield output(pending_ones)
                    yield output(current)
                elif current_lower == "en":
                    if prev_lower not in self.multipliers:
                        if value is not None:
                            yield output(value)
                        if pending_ones is not None:
                            yield output(pending_ones)
                        yield output(current)
                elif current_lower == "dubbel" or current_lower == "drievoudig":
                    if next_lower in self.ones or next_lower in self.zeros:
                        repeats = 2 if current_lower == "dubbel" else 3
                        ones = self.ones.get(next_lower, 0)
                        value = str(value or "") + str(ones) * repeats
                        skip = True
                    else:
                        if value is not None:
                            yield output(value)
                        if pending_ones is not None:
                            yield output(pending_ones)
                        yield output(current)
                elif current_lower == "komma":
                    if next_lower in self.decimals or next_is_numeric:
                        value = str(value or "") + "."
                else:
                    raise ValueError(f"Unexpected token: {current}")
            else:
                raise ValueError(f"Unexpected token: {current}")

        if value is not None:
            yield output(value)
        if pending_ones is not None:
            yield output(pending_ones)

    def preprocess(self, s: str) -> str:
        s = re.sub(r"([a-z])([0-9])", r"\1 \2", s)
        s = re.sub(r"([0-9])([a-z])", r"\1 \2", s)
        s = re.sub(r"([0-9])\s+(e|en|ste)\b", r"\1\2", s)
        return s

    def postprocess(self, s: str) -> str:
        def combine_cents(m: Match):
            try:
                currency = m.group(1)
                integer = m.group(2)
                cents = int(m.group(3))
                return f"{currency}{integer}.{cents:02d}"
            except ValueError:
                return m.string

        def extract_cents(m: Match):
            try:
                return f"¢{int(m.group(1))}"
            except ValueError:
                return m.string

        s = re.sub(r"([€£$¥])([0-9]+) (?:en )?¢([0-9]{1,2})\b", combine_cents, s)
        s = re.sub(r"[€£$¥]0.([0-9]{1,2})\b", extract_cents, s)
        return s

    def __call__(self, s: str) -> str:
        s = self.preprocess(s)
        s = " ".join(word for word in self.process_words(s.split()) if word is not None)
        s = self.postprocess(s)
        return s
