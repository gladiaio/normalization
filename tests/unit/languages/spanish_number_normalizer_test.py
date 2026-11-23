import pytest

from normalization.languages.spanish.number_normalizer import (
    SpanishNumberNormalizer,
)


@pytest.fixture
def normalizer():
    return SpanishNumberNormalizer()


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("veintitres", "23"),
        ("cien", "100"),
        ("doscientos", "200"),
        ("doscientos cincuenta", "250"),
        # A hundreds-block followed by a sub-part before "mil" must keep the
        # thousands multiplier (previously dropped: "doscientos cincuenta mil"
        # returned "250 mil" instead of "250000").
        ("doscientos cincuenta mil", "250000"),
        ("ciento cincuenta mil", "150000"),
        ("novecientos noventa y nueve mil", "999000"),
        ("doscientos cincuenta mil quinientos", "250500"),
    ],
)
def test_spanish_number_normalizer(normalizer, text: str, expected: str):
    assert normalizer(text) == expected
