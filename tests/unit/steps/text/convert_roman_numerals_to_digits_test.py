import pytest

from normalization.languages.base import LanguageOperators
from normalization.languages.norwegian.operators import NorwegianOperators
from normalization.steps.text.convert_roman_numerals_to_digits import (
    ConvertRomanNumeralsToDigitsStep,
)

from .conftest import assert_text_step_registered


def test_step_is_registered():
    assert_text_step_registered(ConvertRomanNumeralsToDigitsStep)


def test_convert_roman_numerals_to_digits_step_converts_roman_numerals_to_digits(
    operators: LanguageOperators,
):
    """
    Test that the convert roman numerals to digits step converts the roman numerals to digits.
    """
    text = "Louis V n'a jamais existé!"
    converted_text = ConvertRomanNumeralsToDigitsStep()(text, operators)
    assert converted_text == "Louis 5 n'a jamais existé!"


def test_convert_roman_numerals_to_digits_step_does_not_convert_other_words(
    operators: LanguageOperators,
):
    """
    Test that the convert roman numerals to digits step does not convert other words.
    """
    text = "Je viens de sortir la v2 de mon app"
    converted_text = ConvertRomanNumeralsToDigitsStep()(text, operators)
    assert converted_text == "Je viens de sortir la v2 de mon app"


def test_convert_roman_numerals_to_digits_step_does_not_convert_other_words_2(
    operators: LanguageOperators,
):
    """
    Test that the convert roman numerals to digits step does not convert other words.
    """
    text = "Je viens de sortir la v2 de mon app"
    converted_text = ConvertRomanNumeralsToDigitsStep()(text, operators)
    assert converted_text == "Je viens de sortir la v2 de mon app"


def test_convert_roman_numerals_to_digits_step_does_not_convert_other_words_3(
    operators: LanguageOperators,
):
    """
    Test that the convert roman numerals to digits step does not convert in words
    """
    text = "Ma soeur s'apelle Violette"
    converted_text = ConvertRomanNumeralsToDigitsStep()(text, operators)
    assert converted_text == "Ma soeur s'apelle Violette"


def test_v_not_converted_when_followed_by_digits_with_space(
    operators: LanguageOperators,
):
    """v followed by digits (with space) should not be treated as roman numeral."""
    text = "api dot endpoint dot v 2"
    converted_text = ConvertRomanNumeralsToDigitsStep()(text, operators)
    assert converted_text == "api dot endpoint dot v 2"


def test_v_not_converted_when_preceded_by_digit(
    operators: LanguageOperators,
):
    """v preceded by a digit should not be treated as roman numeral."""
    text = "12 v motor"
    converted_text = ConvertRomanNumeralsToDigitsStep()(text, operators)
    assert converted_text == "12 v motor"


@pytest.fixture
def uppercase_roman_operators() -> NorwegianOperators:
    return NorwegianOperators()


def test_nordic_lowercase_vi_not_roman(
    uppercase_roman_operators: NorwegianOperators,
) -> None:
    text = "Men vi vet ikke"
    assert ConvertRomanNumeralsToDigitsStep()(text, uppercase_roman_operators) == text


def test_nordic_title_case_vi_not_roman(
    uppercase_roman_operators: NorwegianOperators,
) -> None:
    text = "Vi skal se der"
    assert ConvertRomanNumeralsToDigitsStep()(text, uppercase_roman_operators) == text


def test_nordic_all_caps_vi_is_roman_six(
    uppercase_roman_operators: NorwegianOperators,
) -> None:
    text = "KAPITEL VI i loven"
    assert ConvertRomanNumeralsToDigitsStep()(text, uppercase_roman_operators) == (
        "KAPITEL 6 i loven"
    )
