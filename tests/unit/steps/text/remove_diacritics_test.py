from normalization.languages.default import DefaultOperators
from normalization.steps.text.remove_diacritics import RemoveDiacriticsStep

from .conftest import assert_text_step_registered


def test_step_is_registered():
    assert_text_step_registered(RemoveDiacriticsStep)


def test_remove_diacritics_step_removes_diacritics(operators: DefaultOperators):
    """
    Test that the remove diacritics step removes the diacritics.
    """
    text = "Héllò, wørld!"
    removed_text = RemoveDiacriticsStep()(text, operators)
    assert removed_text == "Hello, world!"
