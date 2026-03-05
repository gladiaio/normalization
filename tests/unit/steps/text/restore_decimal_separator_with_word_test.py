from normalization.languages.base import LanguageOperators
from normalization.steps.text.placeholders import (
    RestoreDecimalSeparatorWithWordStep,
)

from .conftest import assert_text_step_registered


def test_step_is_registered():
    assert_text_step_registered(RestoreDecimalSeparatorWithWordStep)


def test_convert_protected_decimal_separator_to_word_step_converts_protected_decimal_separator_to_word(
    operators: LanguageOperators,
):
    """
    Test that the convert protected decimal separator to word step converts the protected decimal separator to the word decimal.
    """
    text = "100XDECIMALX50 euros"
    replaced_text = RestoreDecimalSeparatorWithWordStep()(text, operators)
    assert replaced_text == "100 point 50 euros"
