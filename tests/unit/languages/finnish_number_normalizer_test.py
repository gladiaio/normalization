import pytest

from normalization.languages.finnish.number_normalizer import FinnishNumberNormalizer
from normalization.languages.finnish.operators import FINNISH_CONFIG


@pytest.fixture
def normalizer() -> FinnishNumberNormalizer:
    return FinnishNumberNormalizer(FINNISH_CONFIG.currency_symbol_to_word)


@pytest.fixture
def normalizer_no_currency() -> FinnishNumberNormalizer:
    return FinnishNumberNormalizer(None)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("kaksi kymmenta viisi", "25"),
        ("kaksi kymmentä viisi", "25"),
        ("sata", "100"),
        ("tuhat", "1000"),
        ("yksi tuhat", "1000"),
        ("kolme miljoonaa", "3000000"),
        ("yksi miljoona", "1000000"),
    ],
)
def test_finnish_spelled_numbers(
    normalizer: FinnishNumberNormalizer, text: str, expected: str
) -> None:
    assert normalizer(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("kymmenen euroa", "10 euroa"),
        ("€50", "50 euros"),
        ("50 €", "50 euros"),
    ],
)
def test_currency_and_spoken_units(
    normalizer: FinnishNumberNormalizer, text: str, expected: str
) -> None:
    assert normalizer(text) == expected


def test_without_currency_config_leaves_currency_symbol(
    normalizer_no_currency: FinnishNumberNormalizer,
) -> None:
    assert normalizer_no_currency("kaksi kymmenta viisi") == "25"
    assert normalizer_no_currency("€10") == "€10"


def test_non_numeric_text_unchanged(normalizer: FinnishNumberNormalizer) -> None:
    text = "tama on tavallista tekstia"
    assert normalizer(text) == text
