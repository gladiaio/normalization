from normalization.languages.default import DefaultOperators
from normalization.steps.text.placeholders import (
    ProtectDecimalSeparatorStep,
)

from .conftest import assert_text_step_registered


def test_step_is_registered():
    assert_text_step_registered(ProtectDecimalSeparatorStep)


def test_protect_decimal_separator_period_separator(operators: DefaultOperators):
    """
    Test that the protect decimal separator step protects the decimal separator.
    """
    operators.config.decimal_separator = "."
    text = "1,234.56"
    protected_text = ProtectDecimalSeparatorStep()(text, operators)
    assert protected_text == "1,234XDECIMALX56"


def test_protect_decimal_separator_comma_separator(operators: DefaultOperators):
    """
    Test that the protect decimal separator step protects the decimal separator.
    """
    operators.config.decimal_separator = ","
    text = "1,234.56"
    protected_text = ProtectDecimalSeparatorStep()(text, operators)
    assert protected_text == "1XDECIMALX234.56"


def test_protect_decimal_separator_multiple_decimals(operators: DefaultOperators):
    """
    Test that the protect decimal separator step protects the decimal separator.
    """
    operators.config.decimal_separator = ","
    text = "1,234.56,789"
    protected_text = ProtectDecimalSeparatorStep()(text, operators)
    assert protected_text == "1XDECIMALX234.56XDECIMALX789"
