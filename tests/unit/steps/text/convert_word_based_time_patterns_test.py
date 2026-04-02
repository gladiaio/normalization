from normalization.languages.english import EnglishOperators
from normalization.steps.text.convert_word_based_time_patterns import (
    ConvertWordBasedTimePatternsStep,
)

from .conftest import assert_text_step_registered


def test_step_is_registered():
    assert_text_step_registered(ConvertWordBasedTimePatternsStep)


def test_hour_with_ampm(english_operators: EnglishOperators):
    step = ConvertWordBasedTimePatternsStep()
    assert step("call at two p.m", english_operators) == "call at 2 pm"


def test_hour_with_am(english_operators: EnglishOperators):
    step = ConvertWordBasedTimePatternsStep()
    assert step("wake up at six a.m", english_operators) == "wake up at 6 am"


def test_hour_and_minute_word_with_ampm(english_operators: EnglishOperators):
    step = ConvertWordBasedTimePatternsStep()
    assert step("meeting at two thirty p.m", english_operators) == "meeting at 2:30 pm"


def test_hour_and_compound_minute_hyphenated(english_operators: EnglishOperators):
    step = ConvertWordBasedTimePatternsStep()
    assert step("at two twenty-one p.m", english_operators) == "at 2:21 pm"


def test_hour_and_compound_minute_spaced(english_operators: EnglishOperators):
    step = ConvertWordBasedTimePatternsStep()
    assert step("at two twenty one pm", english_operators) == "at 2:21 pm"


def test_oclock_with_digit(english_operators: EnglishOperators):
    step = ConvertWordBasedTimePatternsStep()
    assert step("it is 8 o'clock", english_operators) == "it is 8:00"


def test_oclock_ampm_dotted_am(english_operators: EnglishOperators):
    # Mid-sentence so \b matches after the dotted meridiem (same as hour_only convention)
    step = ConvertWordBasedTimePatternsStep()
    assert (
        step("wake up at 6:00 a.m today", english_operators) == "wake up at 6 am today"
    )


def test_oclock_ampm_dotted_pm(english_operators: EnglishOperators):
    step = ConvertWordBasedTimePatternsStep()
    assert (
        step("meeting at 8:00 p.m tomorrow", english_operators)
        == "meeting at 8 pm tomorrow"
    )


def test_oclock_ampm_no_dots(english_operators: EnglishOperators):
    step = ConvertWordBasedTimePatternsStep()
    assert step("meeting at 8:00 pm", english_operators) == "meeting at 8 pm"


def test_oclock_ampm_case_insensitive(english_operators: EnglishOperators):
    step = ConvertWordBasedTimePatternsStep()
    # re.IGNORECASE: uppercase letter is captured as-is; pipeline casefolding normalises before this step
    assert step("call at 3:00 PM", english_operators) == "call at 3 Pm"
