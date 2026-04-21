import pytest

from normalization.languages.dutch.number_normalizer import DutchNumberNormalizer
from normalization.languages.dutch.operators import DUTCH_CONFIG


@pytest.fixture
def normalizer() -> DutchNumberNormalizer:
    return DutchNumberNormalizer(DUTCH_CONFIG.currency_symbol_to_word)


@pytest.fixture
def normalizer_no_currency() -> DutchNumberNormalizer:
    return DutchNumberNormalizer(None)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("vijf en twintig", "25"),
        ("tweehonderd eenendertig", "231"),
        ("drie miljard", "3000000000"),
        ("3 miljard", "3000000000"),
        ("2 miljoen", "2000000"),
        ("2 MILJOEN", "2000000"),
    ],
)
def test_alpha2digit_dutch_spelling_and_large_numbers(
    normalizer: DutchNumberNormalizer, text: str, expected: str
):
    assert normalizer(text) == expected


def test_multi_digit_then_miljoen_not_fully_merged(normalizer: DutchNumberNormalizer):
    """Multi-digit + multiplier is left for alpha2digit; digit is not rewritten to a word."""
    assert normalizer("12 miljoen") == "12 1000000"


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("tien euro", "10 euros"),
        ("honderd euro's", "100 euros"),
        ("€10", "10 euros"),
        ("10 €", "10 euros"),
        ("vijf dollar", "5 dollars"),
        ("$3.50", "3.50 dollars"),
        ("£5", "5 ponden"),
        ("¥200", "200 yens"),
    ],
)
def test_currency_symbols_and_plural_trailing_words(
    normalizer: DutchNumberNormalizer, text: str, expected: str
):
    assert normalizer(text) == expected


def test_without_currency_config_leaves_currency_symbol(
    normalizer_no_currency: DutchNumberNormalizer,
):
    assert normalizer_no_currency("vijf en twintig") == "25"
    assert normalizer_no_currency("€10") == "€10"
    assert normalizer_no_currency("3 miljard") == "3000000000"


def test_non_numeric_text_unchanged(normalizer: DutchNumberNormalizer):
    text = "dit is gewone tekst"
    assert normalizer(text) == text
