import re
from fractions import Fraction
from typing import Iterator, Match

from words2num2 import words2num_sentence


class EnglishNumberNormalizer:
    """Convert any spelled-out numbers into arabic numbers, while handling:

    - remove any commas
    - keep the suffixes such as: `1960s`, `274th`, `32nd`, etc.
    - spell out currency symbols after the number
        e.g. `$20 million` -> `20000000 dollars`
    - spell out `one` and `ones`
    - interpret successive single-digit numbers as nominal: `one oh one` -> `101`

    Derived from OpenAI Whisper's EnglishNumberNormalizer. This is a standalone
    class living in the English language folder.
    """

    def __init__(self):
        self.zeros = {"o", "oh", "zero"}
        self.ones: dict[str, int] = {
            name: i
            for i, name in enumerate(
                [
                    "one",
                    "two",
                    "three",
                    "four",
                    "five",
                    "six",
                    "seven",
                    "eight",
                    "nine",
                    "ten",
                    "eleven",
                    "twelve",
                    "thirteen",
                    "fourteen",
                    "fifteen",
                    "sixteen",
                    "seventeen",
                    "eighteen",
                    "nineteen",
                ],
                start=1,
            )
        }
        self.ones_plural = {
            "sixes" if name == "six" else name + "s": (value, "s")
            for name, value in self.ones.items()
        }
        self.ones_ordinal = {
            "zeroth": (0, "th"),
            "first": (1, "st"),
            "second": (2, "nd"),
            "third": (3, "rd"),
            "fifth": (5, "th"),
            "ninth": (9, "th"),
            "twelfth": (12, "th"),
            **{
                name + ("h" if name.endswith("t") else "th"): (value, "th")
                for name, value in self.ones.items()
                if value > 3 and value not in (5, 9, 12)
            },
        }
        self.ones_suffixed: dict[str, tuple[int, str]] = {
            **self.ones_plural,
            **self.ones_ordinal,
        }

        self.tens = {
            "twenty": 20,
            "thirty": 30,
            "forty": 40,
            "fifty": 50,
            "sixty": 60,
            "seventy": 70,
            "eighty": 80,
            "ninety": 90,
        }
        self.tens_plural = {
            name.replace("y", "ies"): (value, "s") for name, value in self.tens.items()
        }
        self.tens_ordinal = {
            name.replace("y", "ieth"): (value, "th")
            for name, value in self.tens.items()
        }
        self.tens_suffixed = {**self.tens_plural, **self.tens_ordinal}

        self.multipliers = {
            "hundred": 100,
            "thousand": 1_000,
            "million": 1_000_000,
            "billion": 1_000_000_000,
            "trillion": 1_000_000_000_000,
            "quadrillion": 1_000_000_000_000_000,
            "quintillion": 1_000_000_000_000_000_000,
            "sextillion": 1_000_000_000_000_000_000_000,
            "septillion": 1_000_000_000_000_000_000_000_000,
            "octillion": 1_000_000_000_000_000_000_000_000_000,
            "nonillion": 1_000_000_000_000_000_000_000_000_000_000,
            "decillion": 1_000_000_000_000_000_000_000_000_000_000_000,
        }
        self.multipliers_plural = {
            name + "s": (value, "s") for name, value in self.multipliers.items()
        }
        self.multipliers_ordinal = {
            name + "th": (value, "th") for name, value in self.multipliers.items()
        }
        self.multipliers_suffixed = {
            **self.multipliers_plural,
            **self.multipliers_ordinal,
        }
        self.decimals = {*self.ones, *self.tens, *self.zeros}

        self.preceding_prefixers = {
            "minus": "-",
            "negative": "-",
            "plus": "+",
            "positive": "+",
            "zero": "0",
        }
        self.following_prefixers = {
            "pound": "£",
            "pounds": "£",
            "euro": "€",
            "euros": "€",
            "yen": "¥",
            "yens": "¥",
            "dollar": "$",
            "dollars": "$",
            "cent": "¢",
            "cents": "¢",
        }
        self.prefixes = set(
            list(self.preceding_prefixers.values())
            + list(self.following_prefixers.values())
        )
        self.suffixers = {
            "per": {"cent": "%"},
            "percent": "%",
        }
        self.specials = {"and", "double", "triple", "point"}

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
        self.literal_words = {"one", "ones"}
        # The written numbers themselves, without the glue ("and", "point", "double") and
        # without the literals this class turns a trailing digit into ("2.5.1" -> "2.5.one"):
        # what the second pass has left to read, if anything (see __call__).
        written = {
            key
            for mapping in [
                self.zeros,
                self.ones,
                self.ones_suffixed,
                self.tens,
                self.tens_suffixed,
                self.multipliers,
                self.multipliers_suffixed,
            ]
            for key in mapping
        } - self.literal_words
        # longest first, so that "seventeen" is tried before "seven"
        alternatives: list[str] = sorted(
            (re.escape(word) for word in written),
            key=lambda word: len(word),
            reverse=True,
        )
        self._written_number = re.compile(
            r"\b(?:" + "|".join(alternatives) + r")\b", re.IGNORECASE
        )

    def process_words(self, words: list[str]) -> Iterator[str]:  # noqa: C901
        prefix: str | None = None
        value: str | int | None = None
        skip = False

        def to_fraction(s: str | float):
            try:
                return Fraction(s)
            except ValueError:
                return None

        def output(result: str | int):
            nonlocal prefix, value
            result = str(result)
            if prefix is not None:
                result = prefix + result
            value = None
            prefix = None
            return result

        if len(words) == 0:
            return

        for i, current in enumerate(words):
            prev = words[i - 1] if i != 0 else None
            next = words[i + 1] if i != len(words) - 1 else None  # noqa: A001
            if skip:
                skip = False
                continue

            current_lower = current.lower()
            prev_lower = prev.lower() if prev is not None else None
            next_lower = next.lower() if next is not None else None

            next_is_numeric = next is not None and re.match(r"^\d+(\.\d+)?$", next)
            next_next = words[i + 2] if i + 2 < len(words) else None
            next_next_lower = next_next.lower() if next_next is not None else None

            # ASR homophone: "40 for point 5" → "40 four point 5" → 44.5
            if (
                current_lower == "for"
                and next_lower == "point"
                and (
                    value is not None or (prev is not None and re.match(r"^\d+$", prev))
                )
            ):
                current = "four"
                current_lower = "four"

            look_next = next_lower
            if next_lower == "for" and next_next_lower == "point":
                look_next = "four"

            def next_continues_number() -> bool:
                return bool(
                    next_is_numeric
                    or next_lower in self.ones
                    or next_lower in self.tens
                    or next_lower in self.zeros
                    or next_lower in self.multipliers
                    or next_lower in self.ones_suffixed
                    or next_lower in self.tens_suffixed
                    or next_lower == "and"
                    or (next_lower == "for" and next_next_lower == "point")
                )

            if re.match(r"^\d+$", current):
                if value is not None:
                    # "44." + "5" → "44.5" (digit after spoken/decimal point)
                    if isinstance(value, str) and value.endswith("."):
                        value = str(value) + current
                        continue
                    yield output(value)
                    value = None
                # "10 thousand" / "25 hundred" → 10000 / 2500, not bare digits
                # then a leftover multiplier.
                if look_next in self.multipliers:
                    value = int(current)
                    continue
                # "44 point 5" → keep 44 in value so "point" can append "."
                if look_next == "point":
                    value = current
                    continue
                # "2000 and twelve" → keep digits for the following connector.
                if look_next == "and":
                    value = int(current)
                    continue
                # Ones 1–9 after a digit: keep as int so "40 four" → 44.
                # Teens / tens / zeros: keep as string so "20 thirteen" → 2013.
                if look_next in self.ones:
                    if self.ones[look_next] < 10:
                        value = int(current)
                    else:
                        value = current
                    continue
                if look_next in self.tens or look_next in self.zeros:
                    value = current
                    continue
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

                prefix = current[0] if has_prefix else prefix
                if f.denominator == 1:
                    value = f.numerator
                else:
                    value = current_without_prefix
            elif current_lower not in self.words:
                if value is not None:
                    yield output(value)
                yield output(current)
            elif current_lower in self.zeros:
                value = str(value or "") + "0"
            elif current_lower in self.ones:
                ones = self.ones[current_lower]

                if value is None:
                    value = ones
                elif isinstance(value, str) or prev_lower in self.ones:
                    if prev_lower in self.tens and ones < 10:
                        value = value[:-1] + str(ones)  # type: ignore
                    else:
                        value = str(value) + str(ones)
                elif ones < 10:
                    if value % 10 == 0:
                        value += ones
                    else:
                        value = str(value) + str(ones)
                else:
                    if value % 100 == 0:
                        value += ones
                    else:
                        value = str(value) + str(ones)
            elif current_lower in self.ones_suffixed:
                ones, suffix = self.ones_suffixed[current_lower]
                # "eleventh 2000 and twelve" → keep cardinal 11 in-phrase so
                # later digit collapsing can form IDs like 112012.
                if value is None and next_continues_number():
                    value = ones
                    continue
                if value is None:
                    yield output(str(ones) + suffix)
                elif isinstance(value, str) or prev_lower in self.ones:
                    if prev_lower in self.tens and ones < 10:
                        yield output(value[:-1] + str(ones) + suffix)  # type: ignore
                    else:
                        yield output(str(value) + str(ones) + suffix)
                elif ones < 10:
                    if value % 10 == 0:
                        yield output(str(value + ones) + suffix)
                    else:
                        yield output(str(value) + str(ones) + suffix)
                else:
                    if value % 100 == 0:
                        yield output(str(value + ones) + suffix)
                    else:
                        yield output(str(value) + str(ones) + suffix)
                value = None
            elif current_lower in self.tens:
                tens = self.tens[current_lower]
                if value is None:
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
                if value is None:
                    yield output(str(tens) + suffix)
                elif isinstance(value, str):
                    yield output(str(value) + str(tens) + suffix)
                else:
                    if value % 100 == 0:
                        yield output(str(value + tens) + suffix)
                    else:
                        yield output(str(value) + str(tens) + suffix)
            elif current_lower in self.multipliers:
                multiplier = self.multipliers[current_lower]
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

                if next_lower in self.words or next_is_numeric:
                    prefix = self.preceding_prefixers[current_lower]
                else:
                    yield output(current)
            elif current_lower in self.following_prefixers:
                if value is not None:
                    prefix = self.following_prefixers[current_lower]
                    yield output(value)
                else:
                    yield output(current)
            elif current_lower in self.suffixers:
                if value is not None:
                    suffix = self.suffixers[current_lower]
                    if isinstance(suffix, dict):
                        if next in suffix:
                            yield output(str(value) + suffix[next])
                            skip = True
                        else:
                            yield output(value)
                            yield output(current)
                    else:
                        yield output(str(value) + suffix)
                else:
                    yield output(current)
            elif current_lower in self.specials:
                if next_lower not in self.words and not next_is_numeric:
                    if value is not None:
                        yield output(value)
                    yield output(current)
                elif current_lower == "and":
                    # Keep "and" inside a number phrase after multipliers
                    # ("two thousand and twelve") or bare digits
                    # ("2000 and twelve" → 2012).
                    keeps_number_phrase = prev_lower in self.multipliers or (
                        value is not None
                        and isinstance(value, int)
                        and (
                            next_lower in self.ones
                            or next_lower in self.tens
                            or next_lower in self.zeros
                        )
                    )
                    if not keeps_number_phrase:
                        if value is not None:
                            yield output(value)
                        yield output(current)
                elif current_lower == "double" or current_lower == "triple":
                    if next_lower in self.ones or next_lower in self.zeros:
                        repeats = 2 if current_lower == "double" else 3
                        ones = self.ones.get(next_lower, 0)
                        value = str(value or "") + str(ones) * repeats
                        skip = True
                    else:
                        if value is not None:
                            yield output(value)
                        yield output(current)
                elif current_lower == "point":
                    if next_lower in self.decimals or next_is_numeric:
                        value = str(value or "") + "."
                else:
                    raise ValueError(f"Unexpected token: {current}")
            else:
                raise ValueError(f"Unexpected token: {current}")

        if value is not None:
            yield output(value)

    def preprocess(self, s: str) -> str:
        results = []
        segments = re.split(r"\band\s+a\s+half\b", s)
        for i, segment in enumerate(segments):
            if len(segment.strip()) == 0:
                continue
            if i == len(segments) - 1:
                results.append(segment)
            else:
                results.append(segment)
                last_word = segment.rsplit(maxsplit=2)[-1]
                if last_word in self.decimals or last_word in self.multipliers:
                    results.append("point five")
                else:
                    results.append("and a half")

        s = " ".join(results)
        # Common ASR misspelling of "thousand".
        s = re.sub(r"\bthousaond\b", "thousand", s, flags=re.IGNORECASE)
        s = re.sub(r"([a-z])([0-9])", r"\1 \2", s)
        s = re.sub(r"([0-9])([a-z])", r"\1 \2", s)
        s = re.sub(r"([0-9])\s+(st|nd|rd|th|s)\b", r"\1\2", s)
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

        s = re.sub(r"([€£$¥])([0-9]+) (?:and )?¢([0-9]{1,2})\b", combine_cents, s)
        s = re.sub(r"[€£$¥]0.([0-9]{1,2})\b", extract_cents, s)
        s = re.sub(r"\b1(s?)\b", r"one\1", s)
        return s

    def __call__(self, s: str) -> str:
        s = self.preprocess(s)
        s = " ".join(word for word in self.process_words(s.split()) if word is not None)
        s = self.postprocess(s)
        # What this class leaves alone because of the punctuation around it, or because two
        # written numbers sit side by side, words2num2's sentence mode still reads ("that is
        # fifty." -> "that is 50.", "sixty, seventy" -> "60, 70"). It runs on this class's
        # output, so the mixed digit-and-word forms it does not read ("20 thirteen" -> 2013,
        # "25 hundred" -> 2500) keep the value this class gave them. It only runs when a
        # written number is left: on digits and punctuation alone it reads a version or an IP
        # address as a decimal ("2 dot 5 dot 1" -> "2 dot 50 point 1").
        if self._written_number.search(s) is None:
            return s
        return words2num_sentence(s)
