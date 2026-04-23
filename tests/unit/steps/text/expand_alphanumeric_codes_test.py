import pytest

from normalization.languages.base import LanguageOperators
from normalization.languages.norwegian.operators import NorwegianOperators
from normalization.steps.text.expand_alphanumeric_codes import (
    ExpandAlphanumericCodesStep,
)

from .conftest import assert_text_step_registered


def test_step_is_registered() -> None:
    assert_text_step_registered(ExpandAlphanumericCodesStep)


def test_pure_letter_all_caps_not_spaced_when_disabled(
    nordic_acronym_operators: NorwegianOperators,
) -> None:
    step = ExpandAlphanumericCodesStep()
    assert step("SMS til deg", nordic_acronym_operators) == "SMS til deg"
    assert step("CNN", nordic_acronym_operators) == "CNN"


def test_pure_letter_all_caps_spaced_when_enabled(
    operators: LanguageOperators,
) -> None:
    step = ExpandAlphanumericCodesStep()
    assert step("CNN", operators) == "C N N"


def test_mixed_alphanumeric_still_expanded(operators: LanguageOperators) -> None:
    step = ExpandAlphanumericCodesStep()
    assert step("ABC123", operators) == "A B C 1 2 3"


@pytest.fixture
def nordic_acronym_operators() -> NorwegianOperators:
    return NorwegianOperators()
