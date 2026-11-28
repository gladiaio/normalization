import pytest

from normalization.languages.base import LanguageOperators
from normalization.languages.french import FrenchOperators
from normalization.languages.german import GermanOperators
from normalization.languages.norwegian import NorwegianOperators
from normalization.languages.swedish import SwedishOperators
from normalization.steps.text.fold_spelled_ordinals import FoldSpelledOrdinalsStep

from .conftest import assert_text_step_registered


def test_step_is_registered() -> None:
    assert_text_step_registered(FoldSpelledOrdinalsStep)


@pytest.mark.parametrize(
    ("operators_cls", "text", "expected"),
    [
        (FrenchOperators, "le Premier mai", "le 1 mai"),
        (FrenchOperators, "la première fois", "la 1 fois"),
        (GermanOperators, "am ersten Mai", "am 1 Mai"),
        (SwedishOperators, "den tjugoförsta maj", "den 21 maj"),
        (SwedishOperators, "den tjugoandra maj", "den 22 maj"),
        (NorwegianOperators, "den tjueførste mai", "den 21 mai"),
    ],
)
def test_ordinal_folded(operators_cls, text: str, expected: str) -> None:
    assert FoldSpelledOrdinalsStep()(text, operators_cls()) == expected


@pytest.mark.parametrize(
    ("operators_cls", "text"),
    [
        (SwedishOperators, "de andra barnen"),  # "andra" is also "other"
        (NorwegianOperators, "de andre barna"),
        (FrenchOperators, "attendez une seconde"),  # the time unit
        (GermanOperators, "Erstens"),  # "firstly"
        (FrenchOperators, "premierement"),  # part of a longer word
    ],
)
def test_ambiguous_words_left_alone(operators_cls, text: str) -> None:
    assert FoldSpelledOrdinalsStep()(text, operators_cls()) == text


def test_no_op_without_table() -> None:
    assert FoldSpelledOrdinalsStep()("premier", LanguageOperators()) == "premier"
