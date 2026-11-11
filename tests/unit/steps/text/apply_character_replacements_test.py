from normalization.languages.base import LanguageConfig, LanguageOperators
from normalization.steps.text.apply_character_replacements import (
    ApplyCharacterReplacementsStep,
)

from .conftest import assert_text_step_registered


def test_step_is_registered():
    assert_text_step_registered(ApplyCharacterReplacementsStep)


def test_skipped_when_config_is_none(operators: LanguageOperators):
    assert ApplyCharacterReplacementsStep()("abc ـ ٣", operators) == "abc ـ ٣"


def test_replaces_and_deletes_characters():
    operators = LanguageOperators(
        LanguageConfig(
            code="test",
            character_replacements={"a": "b", "-": "", "٣": "3"},
        )
    )
    assert ApplyCharacterReplacementsStep()("a-a ٣", operators) == "bb 3"
