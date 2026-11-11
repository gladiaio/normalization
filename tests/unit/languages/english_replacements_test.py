import pytest

from normalization.languages.english.operators import EnglishOperators


@pytest.fixture
def operators():
    return EnglishOperators()


@pytest.mark.parametrize(
    "joined,split",
    [
        ("nonfiction", "non fiction"),
        ("preexisting", "pre existing"),
    ],
)
def test_joined_compound_maps_to_its_split_form(operators, joined, split):
    """A compound written as one word and the same compound written as two words are the same
    text: the joined form is replaced by the split one."""
    replacements = operators.get_word_replacements()
    assert replacements[joined] == split


def test_joined_compounds_that_are_one_word_stay_untouched(operators):
    """Only the compounds that are also written with a space are replaced."""
    replacements = operators.get_word_replacements()
    assert "nonstop" not in replacements
