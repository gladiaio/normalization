import pytest

from normalization.languages.base import LanguageOperators
from normalization.languages.danish import DanishOperators
from normalization.languages.french import FrenchOperators
from normalization.steps.text.expand_written_numbers_to_digits import (
    ExpandWrittenNumbersToDigitsStep,
)
from normalization.steps.text.expand_written_numbers_to_digits_separating_ordinals import (
    ExpandWrittenNumbersToDigitsSeparatingOrdinalsStep,
)

from .conftest import assert_text_step_registered


def test_step_is_registered() -> None:
    assert_text_step_registered(ExpandWrittenNumbersToDigitsSeparatingOrdinalsStep)


def test_danish_ordinal_is_kept_apart() -> None:
    step = ExpandWrittenNumbersToDigitsSeparatingOrdinalsStep()
    assert step("den første 2 maj", DanishOperators()) == "den ¶ 1. ¶ 2 maj"


def test_expand_written_numbers_to_digits_keeps_danish_ordinal_unmarked() -> None:
    step = ExpandWrittenNumbersToDigitsStep()
    assert step("den første 2 maj", DanishOperators()) == "den 1. 2 maj"


@pytest.mark.parametrize(
    ("operators_cls", "text"),
    [
        (FrenchOperators, "vingt trois pommes et le cinquième"),
        (LanguageOperators, "twenty three"),
    ],
)
def test_without_override_same_as_expand_written_numbers(
    operators_cls: type[LanguageOperators], text: str
) -> None:
    operators = operators_cls()
    assert ExpandWrittenNumbersToDigitsSeparatingOrdinalsStep()(
        text, operators
    ) == ExpandWrittenNumbersToDigitsStep()(text, operators)
