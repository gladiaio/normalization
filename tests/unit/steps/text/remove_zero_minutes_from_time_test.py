from normalization.languages.default import DefaultOperators
from normalization.steps.text.remove_zero_minutes_from_time import (
    RemoveZeroMinutesFromTimeStep,
)

from .conftest import assert_text_step_registered


def test_step_is_registered():
    assert_text_step_registered(RemoveZeroMinutesFromTimeStep)


def test_remove_zero_minutes_from_time_step_removes_zero_minutes(
    operators: DefaultOperators,
):
    """
    Test that the remove zero minutes from time step removes the zero minutes.
    """
    text = "10:00 AM"
    replaced_text = RemoveZeroMinutesFromTimeStep()(text, operators)
    assert replaced_text == "10 AM"
