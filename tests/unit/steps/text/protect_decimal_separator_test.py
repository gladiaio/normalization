from normalization.languages.base import LanguageOperators
from normalization.steps.text.placeholders import (
    ProtectDecimalSeparatorStep,
)

from .conftest import assert_text_step_registered


def test_step_is_registered():
    assert_text_step_registered(ProtectDecimalSeparatorStep)


def test_protect_decimal_separator_period_separator(operators: LanguageOperators):
    """
    Test that the protect decimal separator step protects the decimal separator.
    """
    operators.config.decimal_separator = "."
    text = "1,234.56"
    protected_text = ProtectDecimalSeparatorStep()(text, operators)
    assert protected_text == "1,234XDECIMALX56"


def test_protect_decimal_separator_comma_separator(operators: LanguageOperators):
    """
    Test that the protect decimal separator step protects the decimal separator.
    """
    operators.config.decimal_separator = ","
    text = "1,234.56"
    protected_text = ProtectDecimalSeparatorStep()(text, operators)
    assert protected_text == "1XDECIMALX234.56"


def test_protect_decimal_separator_multiple_decimals(operators: LanguageOperators):
    """
    Test that the protect decimal separator step protects the decimal separator.
    """
    operators.config.decimal_separator = ","
    text = "1,234.56,789"
    protected_text = ProtectDecimalSeparatorStep()(text, operators)
    assert protected_text == "1XDECIMALX234.56XDECIMALX789"


def test_protect_decimal_separator_other_separator_one_or_two_digits(
    operators: LanguageOperators,
):
    """The separator the language does not expect, followed by one or two digits, is a decimal."""
    operators.config.decimal_separator = ","
    step = ProtectDecimalSeparatorStep()
    assert step("6.5 magnitudin", operators) == "6XDECIMALX5 magnitudin"
    assert step("3.50", operators) == "3XDECIMALX50"
    operators.config.decimal_separator = "."
    assert step("6,5 балла", operators) == "6XDECIMALX5 балла"


def test_protect_decimal_separator_other_separator_not_a_decimal(
    operators: LanguageOperators,
):
    """Three digits (a thousands group) and multi-group numbers are left to the other steps."""
    operators.config.decimal_separator = ","
    step = ProtectDecimalSeparatorStep()
    assert step("12.000", operators) == "12.000"
    assert step("1.2.3", operators) == "1.2.3"
    assert step("192.168.1.1", operators) == "192.168.1.1"
    assert step("v1.5", operators) == "v1.5"
