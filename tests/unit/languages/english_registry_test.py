import pytest

from normalization.languages.english.operators import EnglishOperators
from normalization.languages.registery import get_language_registry


@pytest.fixture
def operators():
    return EnglishOperators()


def test_english_is_registered():
    """
    Test that the English operators are registered in the language registry.
    """
    registry = get_language_registry()
    assert "en" in registry


def test_english_registry_entry_produces_english_operators():
    """
    Test that the English operators are produced from the registry.
    """
    registry = get_language_registry()
    instance = registry["en"]()
    assert isinstance(instance, EnglishOperators)


def test_config_code(operators):
    """
    Test that the config code is correct.
    """
    assert operators.config.code == "en"
