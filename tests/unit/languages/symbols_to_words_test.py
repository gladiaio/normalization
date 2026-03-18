import pytest

from normalization.languages.registry import get_language_registry


@pytest.mark.parametrize(
    "language_code,operators_cls", list(get_language_registry().items())
)
def test_symbols_to_words_not_empty(language_code, operators_cls):
    if language_code == "default":
        return
    ops = operators_cls()
    symbols_to_words = ops.config.symbols_to_words
    assert symbols_to_words, f"Symbols to words is empty for language '{language_code}'"


@pytest.mark.parametrize(
    "language_code,operators_cls", list(get_language_registry().items())
)
def test_minimum_symbols_to_words(language_code, operators_cls):
    minimum_symbols_tbd = ["@", ".", "+"]
    ops = operators_cls()
    if language_code == "default":
        return
    symbols_to_words = ops.config.symbols_to_words
    for symbol in minimum_symbols_tbd:
        assert symbol in symbols_to_words, (
            f"Symbol '{symbol}' is not in symbols to words for language '{language_code}'"
        )
