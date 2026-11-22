import unicodedata

from normalization.languages.base import LanguageOperators
from normalization.steps.text.remove_diacritics import RemoveDiacriticsStep

from .conftest import assert_text_step_registered


def test_step_is_registered():
    assert_text_step_registered(RemoveDiacriticsStep)


def test_remove_diacritics_step_removes_diacritics(operators: LanguageOperators):
    """
    Test that the remove diacritics step removes the diacritics.
    """
    text = "Héllò, wørld!"
    removed_text = RemoveDiacriticsStep()(text, operators)
    assert removed_text == "Hello, world!"


def test_remove_diacritics_keeps_marks_of_indic_scripts(operators: LanguageOperators):
    """Devanagari and Bengali vowel signs, viramas and anusvaras are part of the word (#49)."""
    for word in ("लूना", "पहलवानों", "श्रद्धांजलि", "বাংলায়", "গাই"):
        assert RemoveDiacriticsStep()(word, operators) == word


def test_remove_diacritics_keeps_japanese_voicing_marks(operators: LanguageOperators):
    """A dakuten or handakuten makes another kana: です stays です, not てす (#49)."""
    for word in ("です", "が", "パ", "ゴジラ"):
        assert RemoveDiacriticsStep()(word, operators) == word


def test_remove_diacritics_keeps_russian_short_i_and_folds_yo(
    operators: LanguageOperators,
):
    """The breve of й makes another letter; the diaeresis of ё is folded like a Latin one."""
    assert RemoveDiacriticsStep()("двойной Йод", operators) == "двойной Йод"
    assert RemoveDiacriticsStep()("ёлка Ёж", operators) == "елка Еж"


def test_remove_diacritics_drops_hebrew_niqqud(operators: LanguageOperators):
    """Niqqud are vowel points on a complete letter, several on one letter included."""
    assert RemoveDiacriticsStep()("שָׁלוֹם", operators) == "שלום"


def test_remove_diacritics_drops_arabic_harakat(operators: LanguageOperators):
    assert RemoveDiacriticsStep()("مُحَمَّدٌ", operators) == "محمد"


def test_remove_diacritics_drops_a_mark_on_nothing(operators: LanguageOperators):
    """A combining mark with no letter under it (text start, a space, a digit) is noise."""
    assert RemoveDiacriticsStep()("́a 1́ ゙", operators) == "a 1 "


def test_remove_diacritics_leaves_unmarked_text_decomposed_as_before(
    operators: LanguageOperators,
):
    """Only a letter that keeps a mark is recomposed: Hangul stays as NFKD made it."""
    assert RemoveDiacriticsStep()("한국어", operators) == unicodedata.normalize(
        "NFKD", "한국어"
    )
