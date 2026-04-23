from normalization.languages.swedish.operators import SwedishOperators
from normalization.steps.text.remove_standalone_currency_symbols import (
    RemoveStandaloneCurrencySymbolsStep,
)

from .conftest import assert_text_step_registered


def test_step_is_registered() -> None:
    assert_text_step_registered(RemoveStandaloneCurrencySymbolsStep)


def test_multi_char_kr_not_stripped_from_kronor() -> None:
    step = RemoveStandaloneCurrencySymbolsStep()
    op = SwedishOperators()
    assert step("25 kronor", op) == "25 kronor"
