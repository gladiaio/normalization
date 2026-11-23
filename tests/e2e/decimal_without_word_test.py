"""A decimal stays a decimal (#53).

Two causes merged "6.5" or "6,5" into the integer "65": a language with no decimal word got its
separator back as a space, which remove_spaces_between_adjacent_digits then joined; and the
separator a language does not expect ("6.5" in Finnish, "6,5" in a language without a module) was
not protected at all."""

import pytest

from normalization import load_pipeline


@pytest.mark.parametrize(
    ("language", "text", "expected"),
    [
        ("he", "6.5 נקודות", "6.5 נקודות"),
        ("ja", "6.5点", "6.5点"),
        ("pl", "wynik 6.5 punktu", "wynik 6.5 punktu"),
    ],
)
def test_decimal_kept_without_a_decimal_word(
    language: str, text: str, expected: str
) -> None:
    assert load_pipeline("gladia-3", language).normalize(text) == expected


@pytest.mark.parametrize(
    ("language", "dot", "comma", "expected"),
    [
        # Russian has its own module (#52): its decimal separator is the comma.
        ("ru", "6.5 балла", "6,5 балла", "6,5 балла"),
        ("he", "6.5", "6,5", "6.5"),
        ("hi", "6.5", "6,5", "6.5"),
        ("bn", "6.5", "6,5", "6.5"),
        ("fi", "6.5 magnitudin", "6,5 magnitudin", "6 pilkku 5 magnitudin"),
        ("fr", "3.5 euros", "3,5 euros", "3 virgule 5 euros"),
        ("de", "1.5 Meter", "1,5 Meter", "1 komma 5 meter"),
        ("en", "3.5", "3,5", "3 point 5"),
        ("en", "3.50 dollars", "3,50 dollars", "3 point 50 dollars"),
    ],
)
def test_either_separator_gives_the_same_decimal(
    language: str, dot: str, comma: str, expected: str
) -> None:
    pipeline = load_pipeline("gladia-3", language)
    assert pipeline.normalize(dot) == expected
    assert pipeline.normalize(comma) == expected


@pytest.mark.parametrize(
    ("language", "text", "expected"),
    [
        # Three digits after the separator: a thousands group, as before.
        ("da", "12.000", "12000"),
        ("da", "12 000", "12000"),
        ("en", "$1,000,000", "1000000 dollars"),
        ("de", "1.234,56", "1234 komma 56"),
        # Lists keep their own handling.
        ("en", "60, 70", "60 70"),
        # A version number keeps its value instead of becoming one integer.
        ("ru", "802.11a", "802,11a"),
    ],
)
def test_thousands_and_lists_unaffected(
    language: str, text: str, expected: str
) -> None:
    assert load_pipeline("gladia-3", language).normalize(text) == expected


# Outputs of gladia-normalization 0.4.0 (b58bb4f): the languages with a decimal word, and the
# thousands separators, are unchanged.
@pytest.mark.parametrize(
    ("language", "text", "expected"),
    [
        ("en", "6.5 points", "6 point 5 points"),
        ("en", "it costs 1,000 dollars", "it costs 1000 dollars"),
        ("fr", "6,5 points", "6 virgule 5 points"),
        ("de", "6,5 Punkte", "6 komma 5 punkte"),
        ("es", "6,5 puntos", "6 coma 5 puntos"),
        ("fi", "6,5 pistettä", "6 pilkku 5 pistetta"),
        ("pl", "it costs 1,000", "it costs 1000"),
    ],
)
def test_thousands_unchanged(language: str, text: str, expected: str) -> None:
    assert load_pipeline("gladia-3", language).normalize(text) == expected
