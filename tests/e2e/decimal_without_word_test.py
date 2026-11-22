"""A decimal in a language with no decimal word stays a decimal (#53): the separator was restored
as a space, which remove_spaces_between_adjacent_digits then joined ("6.5" -> "65")."""

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
