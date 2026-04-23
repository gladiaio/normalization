import pytest

from normalization.languages.norwegian.operators import NorwegianOperators
from normalization.languages.registry import get_language_registry


@pytest.fixture
def operators() -> NorwegianOperators:
    return NorwegianOperators()


def test_norwegian_is_registered() -> None:
    assert "no" in get_language_registry()


def test_norwegian_registry_produces_norwegian_operators() -> None:
    instance = get_language_registry()["no"]()
    assert isinstance(instance, NorwegianOperators)


def test_config_code(operators: NorwegianOperators) -> None:
    assert operators.config.code == "no"


def test_word_replacements(operators: NorwegianOperators) -> None:
    assert operators.get_word_replacements()["dom"] == "de"
    assert operators.get_word_replacements()["ke"] == "ikke"
    assert operators.get_word_replacements()["ok"] == "okei"
    assert operators.get_word_replacements()["euro"] == "euros"
