from normalization.languages.english import EnglishOperators
from normalization.languages.french import FrenchOperators
from normalization.steps.text.expand_contractions import ExpandContractionsStep

from .conftest import assert_text_step_registered


def test_step_is_registered():
    assert_text_step_registered(ExpandContractionsStep)


def test_expand_contractions_step_english(english_operators: EnglishOperators):
    text = "he ain't gonna"
    formatted_text = ExpandContractionsStep()(text, english_operators)
    assert formatted_text == "he is not going to"


def test_expand_contractions_step_french(french_operators: FrenchOperators):
    text = "j'ai dit c'est bien"
    formatted_text = ExpandContractionsStep()(text, french_operators)
    assert formatted_text == "j'ai dit c'est bien"
