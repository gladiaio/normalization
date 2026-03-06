import pytest

from normalization.languages.base import LanguageOperators
from normalization.languages.registery import get_language_registry


@pytest.fixture
def operators():
    return LanguageOperators()


def test_base_is_registered():
    """
    Test that the base operators are registered in the language registry.
    """
    registry = get_language_registry()
    assert "default" in registry


def test_base_registry_entry_produces_base_operators():
    """
    Test that the English operators are produced from the registry.
    """
    registry = get_language_registry()
    instance = registry["default"]()
    assert isinstance(instance, LanguageOperators)


def test_config_code(operators):
    """
    Test that the config code is correct.
    """
    assert operators.config.code == "default"
