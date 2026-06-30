import pytest

from normalization.languages.english import EnglishOperators
from normalization.steps.text.remove_trailing_apostrophe_space import (
    RemoveTrailingApostropheSpaceStep,
)


@pytest.fixture
def step():
    return RemoveTrailingApostropheSpaceStep()


@pytest.fixture
def operators():
    return EnglishOperators()


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("latvia's population", "latvia population"),
        ("latvia 's population", "latvia population"),
        ("latvia s population", "latvia population"),
        ("the letter s", "the letter s"),
        ("model s car", "model s car"),
        ("tesla model s", "tesla model s"),
    ],
)
def test_remove_trailing_apostrophe_space(step, operators, raw, expected):
    assert step(raw, operators) == expected
