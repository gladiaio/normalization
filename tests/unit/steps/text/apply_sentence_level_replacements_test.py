import pytest

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


@pytest.mark.parametrize(
    "text, expected",
    [
        ("mètres carrés", "m2"),
        ("mètre carré", "m2"),
        ("metres carres", "m2"),
        ("metre carre", "m2"),
        ("metres carre", "m2"),
    ],
)
def test_french_square_metres_phrases_map_to_m2(
    french_operators: FrenchOperators, text: str, expected: str
):
    assert ApplySentenceLevelReplacementsStep()(text, french_operators) == expected


def test_french_bare_metres_is_not_a_sentence_replacement(
    french_operators: FrenchOperators,
):
    assert "metres" not in (french_operators.config.sentence_replacements or {})
    assert ApplySentenceLevelReplacementsStep()("10 metres", french_operators) == (
        "10 metres"
    )
