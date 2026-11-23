from normalization.languages.base import LanguageOperators
from normalization.steps.text.normalize_spelling_variants import (
    NormalizeSpellingVariantsStep,
)

from .conftest import assert_text_step_registered


class _UppercaseOperators(LanguageOperators):
    """A language whose spelling fold is visible: it uppercases the text."""

    def normalize_spelling_variants(self, text: str) -> str:
        return text.upper()


def test_step_is_registered():
    assert_text_step_registered(NormalizeSpellingVariantsStep)


def test_no_op_for_default_operators(operators: LanguageOperators):
    text = "केन्द्रीय café"
    assert NormalizeSpellingVariantsStep()(text, operators) == text


def test_delegates_to_the_language_operators():
    assert NormalizeSpellingVariantsStep()("abc", _UppercaseOperators()) == "ABC"
