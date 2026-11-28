import pytest

from normalization.languages.base import LanguageOperators
from normalization.languages.french import FrenchOperators
from normalization.languages.german import GermanOperators
from normalization.languages.norwegian import NorwegianOperators
from normalization.languages.swedish import SwedishOperators
from normalization.pipeline.base import NormalizationPipeline
from normalization.steps import get_step_registry
from normalization.steps.text.fold_spelled_ordinals import FoldSpelledOrdinalsStep
from normalization.steps.text.placeholders import RestoreNumberListCommasStep
from normalization.steps.text.remove_spaces_between_adjacent_digits import (
    RemoveSpacesBetweenAdjacentDigitsStep,
)

from .conftest import assert_text_step_registered


def test_step_is_registered() -> None:
    assert_text_step_registered(FoldSpelledOrdinalsStep)


@pytest.mark.parametrize(
    ("operators_cls", "text", "expected"),
    [
        (FrenchOperators, "le Premier mai", "le ¶ 1 ¶ mai"),
        (FrenchOperators, "la première fois", "la ¶ 1 ¶ fois"),
        (GermanOperators, "am ersten Mai", "am ¶ 1 ¶ Mai"),
        (SwedishOperators, "den tjugoförsta maj", "den ¶ 21 ¶ maj"),
        (SwedishOperators, "den tjugoandra maj", "den ¶ 22 ¶ maj"),
        (NorwegianOperators, "den tjueførste mai", "den ¶ 21 ¶ mai"),
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


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("le premier 93", "le 1 93"),
        ("au premier 93", "au 1 93"),
        ("le premier 2 mai", "le 1 2 mai"),
        ("le deuxième 4", "le 2 4"),
        ("le 93 premier mai", "le 93 1 mai"),
    ],
)
def test_ordinal_stays_apart_from_next_number(text: str, expected: str) -> None:
    operators = FrenchOperators()
    text = FoldSpelledOrdinalsStep()(text, operators)
    text = RemoveSpacesBetweenAdjacentDigitsStep()(text, operators)
    assert RestoreNumberListCommasStep()(text, operators) == expected


@pytest.mark.parametrize(
    "step_name", ["fold_spelled_ordinals", "strip_ordinal_suffixes"]
)
def test_pipeline_requires_the_mark_restore(step_name: str) -> None:
    registry = get_step_registry()["text"]
    pipeline = NormalizationPipeline(
        name="test",
        operators=FrenchOperators(),
        text_pre_steps=[registry[step_name]()],
    )
    with pytest.raises(ValueError, match="restore_number_list_commas"):
        pipeline.validate()
    pipeline.text_post_steps.append(registry["restore_number_list_commas"]())
    pipeline.validate()
