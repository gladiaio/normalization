import pytest

from normalization.languages.norwegian.number_normalizer import (
    NorwegianNumberNormalizer,
)
from normalization.languages.norwegian.operators import NORWEGIAN_CONFIG


@pytest.fixture
def normalizer() -> NorwegianNumberNormalizer:
    return NorwegianNumberNormalizer(NORWEGIAN_CONFIG.currency_symbol_to_word)


@pytest.fixture
def normalizer_no_currency() -> NorwegianNumberNormalizer:
    return NorwegianNumberNormalizer(None)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("tjue fem", "25"),
        ("tjue og fem", "25"),
        ("tjueen", "21"),
        ("fem hundre femti", "550"),
        ("fem hundre og femti", "550"),
        ("en million", "1000000"),
        ("tre milliarder", "3000000000"),
        ("3 milliard", "3000000000"),
        ("tjue tusen fem", "20005"),
        ("tjue tusen og fem", "20005"),
        ("null", "0"),
        ("femten", "15"),
    ],
)
def test_norwegian_spelled_numbers(
    normalizer: NorwegianNumberNormalizer, text: str, expected: str
) -> None:
    assert normalizer(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("ti euro", "10 euros"),
        ("hundre kroner", "100 kroner"),
        ("€10", "10 euros"),
        ("10 kr", "10 kroner"),
        ("fem dollar", "5 dollars"),
    ],
)
def test_currency_symbols_and_plural_trailing_words(
    normalizer: NorwegianNumberNormalizer, text: str, expected: str
) -> None:
    assert normalizer(text) == expected


def test_without_currency_config_leaves_currency_symbol(
    normalizer_no_currency: NorwegianNumberNormalizer,
) -> None:
    assert normalizer_no_currency("tjue fem") == "25"
    assert normalizer_no_currency("€10") == "€10"
    assert normalizer_no_currency("3 milliard") == "3000000000"


def test_non_numeric_text_unchanged(normalizer: NorwegianNumberNormalizer) -> None:
    text = "dette er vanlig tekst"
    assert normalizer(text) == text


def test_kroner_word_not_treated_as_currency_suffix(
    normalizer: NorwegianNumberNormalizer,
) -> None:
    assert normalizer("25 kroner") == "25 kroner"
