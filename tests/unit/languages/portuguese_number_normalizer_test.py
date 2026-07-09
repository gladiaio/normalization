import pytest

from normalization.languages.portuguese.number_normalizer import (
    PortugueseNumberNormalizer,
)

_DIGIT_WORDS = {
    "zero": "0",
    "um": "1",
    "dois": "2",
    "tres": "3",
    "quatro": "4",
    "cinco": "5",
    "seis": "6",
    "sete": "7",
    "oito": "8",
    "nove": "9",
}


@pytest.fixture
def normalizer():
    return PortugueseNumberNormalizer(_DIGIT_WORDS)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("vinte e tres", "23"),
        ("cem", "100"),
        ("duzentos", "200"),
        ("3 milhoes", "3000000"),
        ("um", "1"),
    ],
)
def test_portuguese_number_normalizer(normalizer, text: str, expected: str):
    assert normalizer(text) == expected
