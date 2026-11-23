import pytest

from normalization import load_pipeline
from normalization.languages.hebrew.operators import HebrewOperators
from normalization.languages.registry import get_language_registry


def test_hebrew_is_registered():
    assert get_language_registry()["he"] is HebrewOperators


@pytest.fixture(scope="module")
def he():
    return load_pipeline("gladia-3", "he")


@pytest.mark.parametrize(
    "text",
    [
        'צה"ל',  # ASCII quotation mark
        "צה״ל",  # U+05F4 gershayim
        "צה”ל",  # right double quotation mark
    ],
)
def test_gershayim_forms_keep_the_abbreviation_whole(he, text):
    assert he.normalize(text) == "צהל"


@pytest.mark.parametrize(
    "text",
    [
        "צ'יפס",  # ASCII apostrophe
        "צ׳יפס",  # U+05F3 geresh
        "צ’יפס",  # right single quotation mark
    ],
)
def test_geresh_forms_keep_the_word_whole(he, text):
    assert he.normalize(text) == "ציפס"


def test_curly_quotes_outside_a_word_stay_punctuation(he):
    assert he.normalize("”שלום”") == "שלום"
    assert he.normalize("’שלום’ לכם") == "שלום לכם"


def test_spoken_and_written_numbers_match(he):
    assert he.normalize("עשרים וחמש") == he.normalize("25") == "25"
    assert he.normalize("חמישה עשר ילדים") == he.normalize("15 ילדים")


@pytest.mark.parametrize(
    ("a", "b"),
    [
        ("מלך", "מלכ"),  # final letter forms are not folded
        ("לחים", "לחם"),  # plene / defective spelling is not folded
    ],
)
def test_distinct_spellings_stay_distinct(he, a, b):
    assert he.normalize(a) != he.normalize(b)
