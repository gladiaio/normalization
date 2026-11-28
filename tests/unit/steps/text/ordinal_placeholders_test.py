import pytest

from normalization.constants.protectors import ordinal_placeholder
from normalization.languages.base import LanguageOperators
from normalization.languages.danish import DanishOperators
from normalization.languages.dutch import DutchOperators
from normalization.languages.english import EnglishOperators
from normalization.languages.french import FrenchOperators
from normalization.languages.german import GermanOperators
from normalization.languages.spanish import SpanishOperators
from normalization.languages.swedish import SwedishOperators
from normalization.pipeline.base import NormalizationPipeline
from normalization.steps import get_step_registry
from normalization.steps.text.placeholders import (
    ProtectDigitOrdinalsStep,
    RestoreOrdinalsStep,
)
from normalization.steps.text.remove_spaces_between_adjacent_digits import (
    RemoveSpacesBetweenAdjacentDigitsStep,
)

from .conftest import assert_text_step_registered


def test_steps_are_registered() -> None:
    assert_text_step_registered(ProtectDigitOrdinalsStep)
    assert_text_step_registered(RestoreOrdinalsStep)


def test_placeholder_has_no_digit() -> None:
    assert not any(c.isdigit() for c in ordinal_placeholder("2024"))


@pytest.mark.parametrize(
    ("operators_cls", "text", "before", "digits", "after"),
    [
        (DanishOperators, "for det 1te", "for det ", "1", ""),
        (DanishOperators, "den 20ende maj", "den ", "20", " maj"),
        (DanishOperators, "den 1. maj", "den ", "1", " maj"),
        (FrenchOperators, "le 1er mai", "le ", "1", " mai"),
        (FrenchOperators, "le 5ème jour", "le ", "5", " jour"),
        (SwedishOperators, "den 1:a maj", "den ", "1", " maj"),
        (SpanishOperators, "el 1º de mayo", "el ", "1", " de mayo"),
        (SpanishOperators, "la 1.ª vez", "la ", "1", " vez"),
    ],
)
def test_digit_ordinal_protected(
    operators_cls, text: str, before: str, digits: str, after: str
) -> None:
    expected = before + ordinal_placeholder(digits) + after
    assert ProtectDigitOrdinalsStep()(text, operators_cls()) == expected


@pytest.mark.parametrize(
    ("operators_cls", "text"),
    [
        (FrenchOperators, "le vol AF1er"),  # a letter before the digits: a code
        (FrenchOperators, "1e5"),  # a letter after the suffix: not an ordinal
        (FrenchOperators, "le 1,5e"),  # a decimal: not an ordinal
        (FrenchOperators, "le 1erx"),
        (GermanOperators, "Ich habe 3."),  # a sentence-final number
        (GermanOperators, "Version 3.5"),
        (EnglishOperators, "the 1st of may"),  # English keeps its own form
        (LanguageOperators, "1er"),
    ],
)
def test_not_an_ordinal_left_alone(operators_cls, text: str) -> None:
    assert ProtectDigitOrdinalsStep()(text, operators_cls()) == text


@pytest.mark.parametrize(
    ("operators_cls", "digits", "expected"),
    [
        (FrenchOperators, "1", "1er"),
        (FrenchOperators, "2", "2e"),
        (FrenchOperators, "21", "21e"),
        (DanishOperators, "1", "1."),
        (GermanOperators, "3", "3."),
        (SwedishOperators, "3", "3:e"),
        (SwedishOperators, "22", "22:a"),
        (SwedishOperators, "11", "11:e"),
        (DutchOperators, "1", "1e"),
        (SpanishOperators, "1", "1º"),
    ],
)
def test_restored_with_canonical_suffix(
    operators_cls, digits: str, expected: str
) -> None:
    text = f"le {ordinal_placeholder(digits)} mai"
    assert RestoreOrdinalsStep()(text, operators_cls()) == f"le {expected} mai"


@pytest.mark.parametrize(
    ("operators_cls", "text", "expected"),
    [
        (FrenchOperators, "page 1er 93", "page 1er 93"),
        (FrenchOperators, "en 2024 1er trimestre", "en 2024 1er trimestre"),
        (DanishOperators, "den 1ste 2 maj", "den 1. 2 maj"),
        (SwedishOperators, "den 1:a 2 maj", "den 1:a 2 maj"),
        (FrenchOperators, "1 2 3", "123"),  # plain digits still collapse
    ],
)
def test_ordinal_never_collapses_with_a_number(
    operators_cls, text: str, expected: str
) -> None:
    operators = operators_cls()
    text = ProtectDigitOrdinalsStep()(text, operators)
    text = RemoveSpacesBetweenAdjacentDigitsStep()(text, operators)
    assert RestoreOrdinalsStep()(text, operators) == expected


@pytest.mark.parametrize(
    "step_name",
    [
        "fold_spelled_ordinals",
        "protect_digit_ordinals",
        "expand_written_numbers_to_digits_protecting_ordinals",
    ],
)
def test_pipeline_requires_restore_ordinals(step_name: str) -> None:
    registry = get_step_registry()["text"]
    pipeline = NormalizationPipeline(
        name="test",
        operators=FrenchOperators(),
        text_pre_steps=[registry[step_name]()],
    )
    with pytest.raises(ValueError, match="restore_ordinals"):
        pipeline.validate()
    pipeline.text_post_steps.append(registry["restore_ordinals"]())
    pipeline.validate()
