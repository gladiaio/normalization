import pytest

from normalization.languages.registry import get_language_registry


def has_multiple_words(key: str) -> bool:
    return " " in key


@pytest.mark.parametrize(
    "language_code,operators_cls", list(get_language_registry().items())
)
def test_word_replacement_keys_are_single_word(language_code, operators_cls):
    ops = operators_cls()
    replacements = ops.get_word_replacements()
    for key, value in replacements.items():
        assert not has_multiple_words(key), (
            f"Word replacement key '{key}' in language '{language_code}' contains a space. "
            "All word-level replacement keys must be a single word. "
            "Multi-word phrase replacements belong in sentence_replacements."
        )
