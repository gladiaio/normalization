from normalization.languages.japanese import JapaneseOperators
from normalization.languages.registry import get_language_registry


def test_japanese_is_registered() -> None:
    assert isinstance(get_language_registry()["ja"](), JapaneseOperators)


def test_config() -> None:
    config = JapaneseOperators().config
    assert config.code == "ja"
    assert config.decimal_separator == "."
    assert config.thousand_separator == ","


def test_expand_written_numbers() -> None:
    assert JapaneseOperators().expand_written_numbers("二十五メートル") == "25メートル"


def test_no_word_replacements() -> None:
    assert JapaneseOperators().get_word_replacements() == {}
