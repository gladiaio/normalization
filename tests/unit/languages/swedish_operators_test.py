import pytest

from normalization.languages.registry import get_language_registry
from normalization.languages.swedish.operators import SwedishOperators


@pytest.fixture
def operators() -> SwedishOperators:
    return SwedishOperators()


def test_swedish_is_registered() -> None:
    assert "sv" in get_language_registry()


def test_swedish_registry_produces_swedish_operators() -> None:
    instance = get_language_registry()["sv"]()
    assert isinstance(instance, SwedishOperators)


def test_config_code(operators: SwedishOperators) -> None:
    assert operators.config.code == "sv"


def test_word_replacements(operators: SwedishOperators) -> None:
    assert operators.get_word_replacements()["mej"] == "mig"
    assert operators.get_word_replacements()["dom"] == "de"
    assert operators.get_word_replacements()["euro"] == "euros"
