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


def test_combining_marks_are_not_word_breaks(operators: LanguageOperators) -> None:
    """A vowel sign, a virama or a niqqud stays with its letter for remove_diacritics (#49)."""
    for word in ("लूना", "श्रद्धांजलि", "বাংলায়", "שָׁלוֹם"):
        assert RemoveSymbolsStep()(word, operators) == word


def test_hebrew_geresh_and_gershayim_inside_a_word_are_removed(
    operators: LanguageOperators,
) -> None:
    for text in ('צה"ל', "צה״ל", "ג'ירפה", "ג׳ירפה"):
        assert " " not in RemoveSymbolsStep()(text, operators)
    assert RemoveSymbolsStep()('צה"ל', operators) == "צהל"


def test_quotes_outside_hebrew_words_still_break(operators: LanguageOperators) -> None:
    assert RemoveSymbolsStep()('it\'s "so"', operators) == "it s  so "
    assert RemoveSymbolsStep()('"שלום"', operators) == " שלום "
