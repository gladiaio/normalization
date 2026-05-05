import pytest

from normalization.languages.swedish.number_normalizer import SwedishNumberNormalizer
from normalization.languages.swedish.operators import SWEDISH_CONFIG


@pytest.fixture
def normalizer() -> SwedishNumberNormalizer:
    return SwedishNumberNormalizer(SWEDISH_CONFIG.currency_symbol_to_word)


@pytest.fixture
def normalizer_no_currency() -> SwedishNumberNormalizer:
    return SwedishNumberNormalizer(None)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("tjugo fem", "25"),
        ("tjugoett", "21"),
        ("tre hundra femtio", "350"),
        ("en miljon", "1000000"),
        ("tre miljarder", "3000000000"),
        ("3 miljard", "3000000000"),
        ("tjugo tusen fem", "20005"),
        ("noll", "0"),
        ("femton", "15"),
    ],
)
def test_swedish_spelled_numbers(
    normalizer: SwedishNumberNormalizer, text: str, expected: str
) -> None:
    assert normalizer(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("tio euro", "10 euros"),
        ("hundra kronor", "100 kronor"),
        ("€10", "10 euros"),
        ("10 kr", "10 kronor"),
        ("fem dollar", "5 dollars"),
    ],
)
def test_currency_symbols_and_plural_trailing_words(
    normalizer: SwedishNumberNormalizer, text: str, expected: str
) -> None:
    assert normalizer(text) == expected


def test_without_currency_config_leaves_currency_symbol(
    normalizer_no_currency: SwedishNumberNormalizer,
) -> None:
    assert normalizer_no_currency("tjugo fem") == "25"
    assert normalizer_no_currency("€10") == "€10"
    assert normalizer_no_currency("3 miljard") == "3000000000"


def test_non_numeric_text_unchanged(normalizer: SwedishNumberNormalizer) -> None:
    text = "det här är vanlig text"
    assert normalizer(text) == text


def test_kronor_word_not_treated_as_currency_suffix(
    normalizer: SwedishNumberNormalizer,
) -> None:
    assert normalizer("25 kronor") == "25 kronor"
