from normalization.languages.base import LanguageOperators
from normalization.languages.english import EnglishOperators
from normalization.languages.norwegian.operators import NorwegianOperators
from normalization.steps.text.remove_symbols import RemoveSymbolsStep

from .conftest import assert_text_step_registered


def test_step_is_registered() -> None:
    assert_text_step_registered(RemoveSymbolsStep)


def test_percent_becomes_word_before_symbol_strip(
    english_operators: EnglishOperators,
) -> None:
    text = RemoveSymbolsStep()("8.75% done", english_operators)
    assert "percent" in text
    assert "%" not in text


def test_percent_skipped_when_not_configured(operators: LanguageOperators) -> None:
    text = RemoveSymbolsStep()("5%", operators)
    assert "%" in text


def test_percent_becomes_norwegian_word_after_numeric_literal() -> None:
    ops = NorwegianOperators()
    text = RemoveSymbolsStep()("8,75% ferdig", ops)
    assert "prosent" in text
    assert "%" not in text


def test_superscript_two_in_square_meter_unit_nfkc_to_ascii_digit(
    operators: LanguageOperators,
) -> None:
    """Superscript ² must become ASCII 2 (NFKC), not be stripped to a space."""
    assert RemoveSymbolsStep()("m²", operators) == "m2"
    assert RemoveSymbolsStep()("50 m²", operators) == "50 m2"
    assert RemoveSymbolsStep()("km²", operators) == "km2"
