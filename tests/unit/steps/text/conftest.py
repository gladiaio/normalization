import pytest

from normalization.languages.base import LanguageOperators
from normalization.languages.dutch import DutchOperators
from normalization.languages.english import EnglishOperators
from normalization.languages.french import FrenchOperators
from normalization.steps import get_step_registry


@pytest.fixture
def operators():
    return LanguageOperators()


@pytest.fixture
def english_operators():
    return EnglishOperators()


@pytest.fixture
def french_operators():
    return FrenchOperators()


@pytest.fixture
def dutch_operators():
    return DutchOperators()


def assert_text_step_registered(step_cls):
    """Verify a text step is properly registered under its name."""
    registry = get_step_registry()
    assert step_cls.name in registry["text"]
    assert registry["text"][step_cls.name] is step_cls
