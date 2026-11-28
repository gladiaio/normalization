import pytest

from normalization.constants.protectors import ordinal_placeholder
from normalization.languages.base import LanguageOperators
from normalization.languages.danish import DanishOperators
from normalization.languages.english import EnglishOperators
from normalization.languages.french import FrenchOperators
from normalization.languages.german import GermanOperators
from normalization.steps.text.expand_written_numbers_to_digits import (
    ExpandWrittenNumbersToDigitsStep,
)
from normalization.steps.text.expand_written_numbers_to_digits_protecting_ordinals import (
    ExpandWrittenNumbersToDigitsProtectingOrdinalsStep,
)

from .conftest import assert_text_step_registered


def test_step_is_registered() -> None:
    assert_text_step_registered(ExpandWrittenNumbersToDigitsProtectingOrdinalsStep)


def test_danish_ordinal_is_held() -> None:
    step = ExpandWrittenNumbersToDigitsProtectingOrdinalsStep()
    assert step("den første 2 maj", DanishOperators()) == (
        f"den {ordinal_placeholder('1')} 2 maj"
    )


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("am dritten Mai", f"am {ordinal_placeholder('3')} Mai"),
        ("am dritten.", f"am {ordinal_placeholder('3')}."),
        # A cardinal before a period stays a cardinal, apart from the period.
        ("Ich habe drei. Dann", "Ich habe 3 . Dann"),
        ("Das ist gut. Dann", "Das ist gut. Dann"),
    ],
)
def test_german_ordinal_is_held(text: str, expected: str) -> None:
    step = ExpandWrittenNumbersToDigitsProtectingOrdinalsStep()
    assert step(text, GermanOperators()) == expected


def test_english_ordinal_before_a_number_stays_an_ordinal() -> None:
    step = ExpandWrittenNumbersToDigitsProtectingOrdinalsStep()
    assert step("the first 2 May", EnglishOperators()) == "the 1st 2 May"
    assert ExpandWrittenNumbersToDigitsStep()(
        "the first 2 May", EnglishOperators()
    ) == ("the one 2 May")


def test_expand_written_numbers_to_digits_keeps_danish_ordinal() -> None:
    step = ExpandWrittenNumbersToDigitsStep()
    assert step("den første 2 maj", DanishOperators()) == "den 1. 2 maj"


@pytest.mark.parametrize(
    ("operators_cls", "text"),
    [
        (FrenchOperators, "vingt trois pommes et le cinquième"),
        (LanguageOperators, "twenty three"),
    ],
)
def test_without_override_same_as_expand_written_numbers(
    operators_cls: type[LanguageOperators], text: str
) -> None:
    operators = operators_cls()
    assert ExpandWrittenNumbersToDigitsProtectingOrdinalsStep()(
        text, operators
    ) == ExpandWrittenNumbersToDigitsStep()(text, operators)
