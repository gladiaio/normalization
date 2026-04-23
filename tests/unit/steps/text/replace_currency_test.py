from normalization.languages.english import EnglishOperators
from normalization.languages.swedish.operators import SwedishOperators
from normalization.steps.text.replace_currency import ReplaceCurrencyStep

from .conftest import assert_text_step_registered


def test_step_is_registered() -> None:
    assert_text_step_registered(ReplaceCurrencyStep)


def test_replace_currency_step_replaces_currency(english_operators: EnglishOperators):
    """
    Test that the replace currency step replaces the currency.
    """
    text = "100€"
    replaced_text = ReplaceCurrencyStep()(text, english_operators)
    assert replaced_text == "100 euros"


def test_replace_currency_kr_uses_word_boundaries() -> None:
    """``kr`` must not match the prefix of ``kronor``."""
    step = ReplaceCurrencyStep()
    op = SwedishOperators()
    assert step("25 kronor", op) == "25 kronor"
    assert step("25 kr", op) == "25 kronor"


def test_replace_currency_step_replaces_currency_with_decimal_separator(
    english_operators: EnglishOperators,
):
    """
    Test that the replace currency step replaces the currency with the decimal separator.
    """
    text = "100.50€"
    replaced_text = ReplaceCurrencyStep()(text, english_operators)
    assert replaced_text == "100.50 euros"
