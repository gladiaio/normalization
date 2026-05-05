import pytest

from normalization.languages.finnish.operators import FinnishOperators
from normalization.languages.registry import get_language_registry


@pytest.fixture
def operators() -> FinnishOperators:
    return FinnishOperators()


def test_finnish_is_registered() -> None:
    assert "fi" in get_language_registry()


def test_finnish_registry_produces_finnish_operators() -> None:
    instance = get_language_registry()["fi"]()
    assert isinstance(instance, FinnishOperators)


def test_config_code(operators: FinnishOperators) -> None:
    assert operators.config.code == "fi"


def test_word_replacements(operators: FinnishOperators) -> None:
    assert operators.get_word_replacements()["ma"] == "mina"
    assert operators.get_word_replacements()["ok"] == "okei"
    assert operators.get_word_replacements()["juu"] == "joo"
    assert operators.get_word_replacements()["euro"] == "euros"
