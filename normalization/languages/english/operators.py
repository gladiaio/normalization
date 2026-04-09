import re
from typing import cast

import contractions

from normalization.languages.base import LanguageConfig, LanguageOperators
from normalization.languages.english.number_normalizer import EnglishNumberNormalizer
from normalization.languages.english.replacements import ENGLISH_REPLACEMENTS
from normalization.languages.english.sentence_replacements import (
    ENGLISH_SENTENCE_REPLACEMENTS,
)
from normalization.languages.registry import register_language

# Single digits 1-9 as words: shared by _TIME_WORDS, digit_words, and
# get_compound_minutes() so each word is defined exactly once.
_ONE_TO_NINE: dict[str, str] = {
    "one": "1",
    "two": "2",
    "three": "3",
    "four": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8",
    "nine": "9",
}

# All spoken time values: clock hours (1-12) and minute-worth values (13-50).
# Covers both o'clock patterns and "eight thirty"-style patterns.
_TIME_WORDS: dict[str, str] = {
    **_ONE_TO_NINE,
    "ten": "10",
    "eleven": "11",
    "twelve": "12",
    "noon": "12",
    "midnight": "12",
    "thirteen": "13",
    "fourteen": "14",
    "fifteen": "15",
    "sixteen": "16",
    "seventeen": "17",
    "eighteen": "18",
    "nineteen": "19",
    "twenty": "20",
    "thirty": "30",
    "forty": "40",
    "fifty": "50",
}

ENGLISH_CONFIG = LanguageConfig(
    code="en",
    decimal_separator=".",
    decimal_word="point",
    thousand_separator=",",
    symbols_to_words={
        "@": "at",
        ".": "dot",
        "+": "plus",
        "=": "equals",
        ">": "greater than",
        "<": "less than",
        "°": "degree",
        "°C": "degree celsius",
        "°F": "degree fahrenheit",
        "%": "percent",
    },
    currency_symbol_to_word={
        "€": "euros",
        "$": "dollars",
        "£": "pounds",
        "¢": "cents",
        "¥": "yens",
    },
    filler_words=[
        "um",
        "uh",
        "uhm",
        "ooh",
        "yeah",
        "yep",
        "yup",
        "hmm",
        "huh",
        "mhm",
        "mm",
        "mmm",
    ],
    oclock_word="o'clock",
    time_words=_TIME_WORDS,
    sentence_replacements=ENGLISH_SENTENCE_REPLACEMENTS,
    # _ONE_TO_NINE (1-9) plus zero and its spoken aliases ("oh", "o").
    digit_words={"zero": "0", "oh": "0", "o": "0", **_ONE_TO_NINE},
    # Full number-word vocabulary used for contextual detection.
    # Reuses _TIME_WORDS (1-50) to avoid repeating every word,
    # then appends zero/aliases and the remaining tens (60-90) and scale words.
    number_words=[
        "zero",
        "oh",
        "o",
        *_TIME_WORDS,  # one … fifty
        "sixty",
        "seventy",
        "eighty",
        "ninety",
        "hundred",
        "thousand",
        "million",
        "billion",
        "trillion",
    ],
    plus_word="plus",
    ordinal_suffixes=["st", "nd", "rd", "th"],
    am_word="am",
    pm_word="pm",
)


@register_language
class EnglishOperators(LanguageOperators):
    def __init__(self):
        super().__init__(ENGLISH_CONFIG)
        self._number_normalizer = EnglishNumberNormalizer()

    def expand_contractions(self, text: str) -> str:
        text = re.sub(
            r"\bhe ain't gonna\b", "he is not going to", text, flags=re.IGNORECASE
        )
        text = re.sub(
            r"\bshe ain't gonna\b", "she is not going to", text, flags=re.IGNORECASE
        )
        text = re.sub(
            r"\bit ain't gonna\b", "it is not going to", text, flags=re.IGNORECASE
        )
        text = re.sub(r"\bi'ma\b", "i am going to", text, flags=re.IGNORECASE)
        text = cast(str, contractions.fix(text, slang=True))
        return text

    def get_compound_minutes(self) -> dict[str, str]:
        """Build compound minute expressions: 'twenty-one'/'twenty one' → '21', … 'fifty-nine' → '59'.

        Uses _ONE_TO_NINE for the ones component so no word is listed twice.
        Both hyphenated and spaced forms are produced (English uses both).
        """
        result: dict[str, str] = {}
        for tens_word, tens_val in [
            ("twenty", 20),
            ("thirty", 30),
            ("forty", 40),
            ("fifty", 50),
        ]:
            for ones_word, ones_str in _ONE_TO_NINE.items():
                value = str(tens_val + int(ones_str))
                result[f"{tens_word}-{ones_word}"] = value
                result[f"{tens_word} {ones_word}"] = value
        return result

    def normalize_numeric_time_formats(self, text: str) -> str:
        def _format_dot_time(match: re.Match) -> str:
            hour = str(int(match.group(1)))
            minute = match.group(2)
            ampm = match.group(3).lower()
            return f"{hour}:{minute} {ampm}m"

        text = re.sub(
            r"\b(\d{1,2})\.(\d{2})\s*([ap])\.?m\.?\b",
            _format_dot_time,
            text,
            flags=re.IGNORECASE,
        )

        def _format_colon_time(match: re.Match) -> str:
            hour = str(int(match.group(1)))
            minute = match.group(2)
            ampm = match.group(3).lower()
            return f"{hour}:{minute} {ampm}m"

        text = re.sub(
            r"\b(\d{1,2}):(\d{2})([ap])m\b",
            _format_colon_time,
            text,
            flags=re.IGNORECASE,
        )
        return text

    def fix_one_word_in_numeric_contexts(self, text: str) -> str:
        text = re.sub(r"(\d+)\s+one\s+one\b", r"\1 1 1", text)
        text = re.sub(r"\bone\s+one\s+(\d)", r"1 1 \1", text)
        text = re.sub(r"(\d+)\s+one\s+(\d)", r"\1 1 \2", text)
        text = re.sub(r"(\d+)\s+one\b", r"\1 1", text)
        text = re.sub(r"\b(\d+)one\b", r"\1 1", text)
        text = re.sub(r"\bone\s+(\d)", r"1 \1", text)
        text = re.sub(r"^one\s+(?=[a-z])", "1 ", text)
        return text

    def get_word_replacements(self) -> dict[str, str]:
        return ENGLISH_REPLACEMENTS

    def expand_written_numbers(self, text: str) -> str:
        return self._number_normalizer(text)
