import pytest

from normalization.languages.dutch.operators import DutchOperators
from normalization.languages.registry import get_language_registry


@pytest.fixture
def operators():
    return DutchOperators()


def test_dutch_is_registered():
    assert "nl" in get_language_registry()


def test_dutch_registry_produces_dutch_operators():
    instance = get_language_registry()["nl"]()
    assert isinstance(instance, DutchOperators)


def test_expand_flemish_clitics(operators):
    assert operators.expand_contractions("ik zeg 't zo") == "ik zeg het zo"
    assert operators.expand_contractions("zeg ’t zo") == "zeg het zo"
    assert operators.expand_contractions("'k kom morgen") == "ik kom morgen"
    assert operators.expand_contractions("is 'r nog") == "is er nog"
    assert operators.expand_contractions("'n beetje") == "een beetje"
    assert operators.expand_contractions("zie je 'm") == "zie je hem"
    assert operators.expand_contractions("dat 's goed") == "dat is goed"


def test_expand_clitic_s_not_possessive_after_word(operators):
    assert operators.expand_contractions("Jan's auto") == "Jan's auto"


def test_expand_temporal_s_to_des(operators):
    assert operators.expand_contractions("'s ochtends vroeg") == "des ochtends vroeg"
    assert operators.expand_contractions("'S Avonds laat") == "des avonds laat"


def test_config_sentence_replacements(operators):
    assert operators.config.sentence_replacements is not None
    assert operators.config.sentence_replacements["kollega"] == "collega"


def test_word_replacements(operators):
    assert operators.get_word_replacements()["ge"] == "je"
    assert operators.get_word_replacements()["da"] == "dat"
    assert operators.get_word_replacements()["u"] == "je"
    assert operators.get_word_replacements()["uw"] == "je"
    assert operators.get_word_replacements()["okee"] == "oke"
    assert operators.get_word_replacements()["euro"] == "euros"
