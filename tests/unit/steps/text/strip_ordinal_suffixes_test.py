import pytest

from normalization.languages.base import LanguageOperators
from normalization.languages.danish import DanishOperators
from normalization.languages.english import EnglishOperators
from normalization.languages.french import FrenchOperators
from normalization.languages.spanish import SpanishOperators
from normalization.languages.swedish import SwedishOperators
from normalization.steps.text.placeholders import RestoreNumberListCommasStep
from normalization.steps.text.remove_spaces_between_adjacent_digits import (
    RemoveSpacesBetweenAdjacentDigitsStep,
)
from normalization.steps.text.strip_ordinal_suffixes import StripOrdinalSuffixesStep

from .conftest import assert_text_step_registered


def test_step_is_registered() -> None:
    assert_text_step_registered(StripOrdinalSuffixesStep)


@pytest.mark.parametrize(
    ("operators_cls", "text", "expected"),
    [
        (DanishOperators, "for det 1te", "for det ¶ 1 ¶"),
        (DanishOperators, "den 20ende maj", "den ¶ 20 ¶ maj"),
        (FrenchOperators, "le 1er mai", "le ¶ 1 ¶ mai"),
        (FrenchOperators, "le 5ème jour", "le ¶ 5 ¶ jour"),
        (SwedishOperators, "den 1:a maj", "den ¶ 1 ¶ maj"),
        (SpanishOperators, "el 1º de mayo", "el ¶ 1 ¶ de mayo"),
        (SpanishOperators, "la 1.ª vez", "la ¶ 1 ¶ vez"),
    ],
)
def test_suffix_dropped(operators_cls, text: str, expected: str) -> None:
    assert StripOrdinalSuffixesStep()(text, operators_cls()) == expected


@pytest.mark.parametrize(
    "text",
    [
        "le vol AF1er",  # a letter before the digits: a code
        "1e5",  # a letter after the suffix: not an ordinal
        "le 1,5e",  # a decimal: not an ordinal
        "le 1erx",
    ],
)
def test_codes_left_alone(text: str) -> None:
    assert StripOrdinalSuffixesStep()(text, FrenchOperators()) == text


def test_english_keeps_its_suffix() -> None:
    assert StripOrdinalSuffixesStep()("the 1st of may", EnglishOperators()) == (
        "the 1st of may"
    )


def test_no_op_without_suffixes() -> None:
    assert StripOrdinalSuffixesStep()("1er", LanguageOperators()) == "1er"


@pytest.mark.parametrize(
    ("operators_cls", "text", "expected"),
    [
        (FrenchOperators, "page 1er 93", "page 1 93"),
        (FrenchOperators, "le 2e 4", "le 2 4"),
        (DanishOperators, "den 1ste 2 maj", "den 1 2 maj"),
        (SwedishOperators, "den 1:a 2 maj", "den 1 2 maj"),
        (FrenchOperators, "1 2 3", "123"),  # plain digits still collapse
    ],
)
def test_ordinal_stays_apart_from_next_number(
    operators_cls, text: str, expected: str
) -> None:
    operators = operators_cls()
    text = StripOrdinalSuffixesStep()(text, operators)
    text = RemoveSpacesBetweenAdjacentDigitsStep()(text, operators)
    assert RestoreNumberListCommasStep()(text, operators) == expected
