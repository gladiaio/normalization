import pytest

from normalization.languages.danish.operators import DanishOperators
from normalization.languages.registry import get_language_registry


@pytest.fixture
def operators() -> DanishOperators:
    return DanishOperators()


def test_danish_is_registered() -> None:
    assert "da" in get_language_registry()


def test_danish_registry_produces_danish_operators() -> None:
    instance = get_language_registry()["da"]()
    assert isinstance(instance, DanishOperators)


def test_config_code(operators: DanishOperators) -> None:
    assert operators.config.code == "da"


def test_word_replacements(operators: DanishOperators) -> None:
    assert operators.get_word_replacements()["krone"] == "kroner"
    assert "euro" not in operators.get_word_replacements()


@pytest.mark.parametrize(
    ("variant", "canonical"),
    [
        # dobbeltformer spelling variants
        ("grøntsager", "grønsager"),
        ("handikap", "handicap"),
        ("taknemmelig", "taknemlig"),
        # abbreviations
        ("dvs", "det vil sige"),
        ("fx", "for eksempel"),
        ("pct", "procent"),
        ("osv", "og så videre"),
        ("ok", "okay"),
    ],
)
def test_danish_word_replacements(
    operators: DanishOperators, variant: str, canonical: str
) -> None:
    replacements = operators.get_word_replacements()
    assert replacements[variant] == canonical


@pytest.mark.parametrize(
    ("phrase", "canonical"),
    [
        ("selv om", "selvom"),
        ("til lykke", "tillykke"),
        ("ingen sinde", "ingensinde"),
        ("ingen ting", "ingenting"),
        ("immer væk", "immervæk"),
    ],
)
def test_danish_sentence_replacements(phrase: str, canonical: str) -> None:
    from normalization.languages.danish.sentence_replacements import (
        DANISH_SENTENCE_REPLACEMENTS,
    )

    assert DANISH_SENTENCE_REPLACEMENTS[phrase] == canonical
