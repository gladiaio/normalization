from normalization.languages.french import FrenchOperators
from normalization.steps.text.apply_sentence_level_replacements import (
    ApplySentenceLevelReplacementsStep,
)

from .conftest import assert_text_step_registered


def test_step_is_registered():
    assert_text_step_registered(ApplySentenceLevelReplacementsStep)


def test_apply_sentence_level_replacements_step_french_pour_100(
    french_operators: FrenchOperators,
):
    text = "pour 100 de réduction"
    formatted_text = ApplySentenceLevelReplacementsStep()(text, french_operators)
    assert formatted_text == "pourcent de réduction"
