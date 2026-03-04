from normalization.languages.english import EnglishOperators
from normalization.steps.text.convert_oclock_to_numeric_time import (
    ConvertOclockToNumericTimeStep,
)

from .conftest import assert_text_step_registered


def test_step_is_registered():
    assert_text_step_registered(ConvertOclockToNumericTimeStep)


def test_convert_oclock_to_numeric_time_step_converts_oclock_to_numeric_time(
    english_operators: EnglishOperators,
):
    """
    Test that the format time patterns with ampm step formats the time patterns with ampm.
    """
    text = "it is 8 o'clock"
    formatted_text = ConvertOclockToNumericTimeStep()(text, english_operators)
    assert formatted_text == "it is 8:00"


def test_convert_oclock_to_numeric_time_step_does_not_convert_other_words(
    english_operators: EnglishOperators,
):
    """
    Test that the convert oclock to numeric time step does not convert other words.
    """
    text = "what does o'clock mean"
    formatted_text = ConvertOclockToNumericTimeStep()(text, english_operators)
    assert formatted_text == "what does o'clock mean"
