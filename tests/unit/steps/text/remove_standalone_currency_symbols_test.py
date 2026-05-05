from normalization.languages.norwegian.operators import NorwegianOperators
from normalization.languages.swedish.operators import SwedishOperators
from normalization.steps.text.remove_standalone_currency_symbols import (
    RemoveStandaloneCurrencySymbolsStep,
)

from .conftest import assert_text_step_registered


def test_step_is_registered() -> None:
    assert_text_step_registered(RemoveStandaloneCurrencySymbolsStep)


def test_multi_char_kr_does_not_match_letters_inside_words() -> None:
    ops = NorwegianOperators()
    step = RemoveStandaloneCurrencySymbolsStep()
    assert step("punkt", ops) == "punkt"
    assert step("euros", ops) == "euros"


def test_multi_char_kr_kept_when_touching_digit() -> None:
    ops = NorwegianOperators()
    step = RemoveStandaloneCurrencySymbolsStep()
    assert step("10 kr", ops) == "10 kr"


def test_standalone_kr_token_removed_when_not_near_digits() -> None:
    ops = NorwegianOperators()
    step = RemoveStandaloneCurrencySymbolsStep()
    assert step("pris er kr i dag", ops) == "pris er  i dag"


def test_multi_char_kr_not_stripped_from_kronor() -> None:
    step = RemoveStandaloneCurrencySymbolsStep()
    op = SwedishOperators()
    assert step("25 kronor", op) == "25 kronor"
