import pytest

from normalization.languages.english.number_normalizer import EnglishNumberNormalizer
from normalization.pipeline.loader import load_pipeline

_ONES_UNITS: dict[str, int] = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
}

_TEENS: dict[str, int] = {
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
    "thirteen": 13,
    "fourteen": 14,
    "fifteen": 15,
    "sixteen": 16,
    "seventeen": 17,
    "eighteen": 18,
    "nineteen": 19,
}

_TENS: dict[str, int] = {
    "twenty": 20,
    "thirty": 30,
    "forty": 40,
    "fifty": 50,
    "sixty": 60,
    "seventy": 70,
    "eighty": 80,
    "ninety": 90,
}

_ROUND_TENS = (10, 20, 30, 40, 50, 60, 70, 80, 90)
_LEADING_DIGITS = (2, 10, 20, 30, 99)


@pytest.fixture
def normalizer() -> EnglishNumberNormalizer:
    return EnglishNumberNormalizer()


@pytest.mark.parametrize(
    ("digit", "word", "word_value"),
    [
        (digit, word, value)
        for digit in _ROUND_TENS
        for word, value in _ONES_UNITS.items()
    ],
)
def test_round_digit_plus_unit_adds(
    normalizer: EnglishNumberNormalizer,
    digit: int,
    word: str,
    word_value: int,
) -> None:
    """'40 four' → '44', '30 two' → '32' (tens + ones), not concatenation."""
    assert normalizer(f"{digit} {word}") == str(digit + word_value)


@pytest.mark.parametrize(
    ("digit", "word", "word_value"),
    [
        (digit, word, value)
        for digit in _LEADING_DIGITS
        for word, value in {**_TEENS, **_TENS}.items()
    ],
)
def test_digit_plus_teen_or_tens_concatenates(
    normalizer: EnglishNumberNormalizer,
    digit: int,
    word: str,
    word_value: int,
) -> None:
    """'20 thirteen' → '2013', '20 twenty' → '2020'."""
    assert normalizer(f"{digit} {word}") == f"{digit}{word_value}"


@pytest.mark.parametrize("digit", range(1, 100))
def test_digit_plus_hundred_multiplies(
    normalizer: EnglishNumberNormalizer, digit: int
) -> None:
    """'20 hundred' → '2000', '25 hundred' → '2500', … for every 1–99."""
    assert normalizer(f"{digit} hundred") == str(digit * 100)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("1 thousand", "1000"),
        ("10 thousand", "10000"),
        ("25 thousand", "25000"),
        ("100 thousand", "100000"),
        ("1 million", "1000000"),
        ("20 million", "20000000"),
        ("25 million", "25000000"),
    ],
)
def test_digit_plus_large_multiplier(
    normalizer: EnglishNumberNormalizer, text: str, expected: str
) -> None:
    assert normalizer(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        # "for" is ASR for "four": 40 + 4 + .5
        ("40 for point 5", "44.5"),
        ("40 four point 5", "44.5"),
        ("44 point 5", "44.5"),
        ("eleventh 2000 and twelve", "11 2012"),
        ("eleventh 2 thousand and twelve", "11 2012"),
        ("eleventh 2 thousaond and twelve", "11 2012"),
    ],
)
def test_asr_number_phrase_forms(
    normalizer: EnglishNumberNormalizer, text: str, expected: str
) -> None:
    assert normalizer(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("40 for point 5", "44 point 5"),
        ("40 four point 5", "44 point 5"),
        ("eleventh 2000 and twelve", "112012"),
        ("eleventh 2 thousand and twelve", "112012"),
        ("eleventh 2 thousaond and twelve", "112012"),
        ("25 hundred", "2500"),
        ("35 hundred", "3500"),
        ("20 hundred", "2000"),
        ("20 thirteen", "2013"),
        ("30 two", "32"),
        ("20 one", "21"),
        ("20 twenty", "2020"),
        ("10 thousand", "10000"),
    ],
)
def test_words_to_num_through_gladia_3_pipeline(text: str, expected: str) -> None:
    pipeline = load_pipeline("gladia-3", "en")
    assert pipeline.normalize(text) == expected


def test_standalone_ordinal_still_keeps_suffix(
    normalizer: EnglishNumberNormalizer,
) -> None:
    assert normalizer("eleventh") == "11th"
    assert normalizer("first") == "1st"


def test_ninth_ordinal_normalizes(
    normalizer: EnglishNumberNormalizer,
) -> None:
    # "nine" is irregular: the ordinal is "ninth", not "nineth". It was missing
    # from the ordinal table, so the generic "<word>th" rule produced the key
    # "nineth" and real "ninth" input was left unconverted.
    assert normalizer("ninth") == "9th"
    assert normalizer("twenty ninth") == "29th"


@pytest.mark.parametrize(
    "text, expected",
    [
        ("ninth", "9th"),
        ("twenty ninth", "29th"),
        ("one hundred ninth", "109th"),
    ],
)
def test_ninth_ordinal_through_gladia_3_pipeline(text: str, expected: str) -> None:
    pipeline = load_pipeline("gladia-3", "en")
    assert pipeline.normalize(text) == expected


def test_for_not_rewritten_outside_number_point_context(
    normalizer: EnglishNumberNormalizer,
) -> None:
    assert normalizer("for example") == "for example"
    assert normalizer("40 for example") == "40 for example"
