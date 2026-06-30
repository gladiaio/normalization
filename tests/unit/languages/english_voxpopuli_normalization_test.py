import pytest

from normalization.languages.english.number_normalizer import EnglishNumberNormalizer
from normalization.pipeline.loader import load_pipeline


@pytest.fixture
def pipeline():
    return load_pipeline("gladia-3", "en")


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("pttering", "pottering"),
        ("puttering", "pottering"),
        ("putttering", "pottering"),
        ("puttrich", "pottering"),
        ("guantnamo", "guantanamo"),
    ],
)
def test_voxpopuli_word_aliases(pipeline, raw, expected):
    assert pipeline.normalize(raw) == expected


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("50%", "50 percent"),
        (
            "more than fifteen of latvia population",
            "more than 15 percent of latvia population",
        ),
        (
            "fifteen of latvia s population",
            "15 percent of latvia population",
        ),
        ("15 of 20 people", "15 of 20 people"),
        ("5 of the members", "5 of the members"),
        ("rule 142 of the agenda", "article 142 of the agenda"),
        ("article 142 of chapter 3", "article 142 of chapter 3"),
    ],
)
def test_percent_of_patterns(pipeline, raw, expected):
    assert pipeline.normalize(raw) == expected


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("rule 142 2a 2b", "article 142 2a 2b"),
        ("article 142 2A 2B", "article 142 2a 2b"),
    ],
)
def test_parliamentary_references(pipeline, raw, expected):
    assert pipeline.normalize(raw) == expected


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("latvia's population", "latvia population"),
        ("latvia s population", "latvia population"),
    ],
)
def test_possessive_cleanup(pipeline, raw, expected):
    assert pipeline.normalize(raw) == expected


def test_hundred_compound_zero_means_thousands():
    normalizer = EnglishNumberNormalizer()
    assert normalizer("three hundred and seventy two zero") == "372000"
    assert normalizer("five hundred zero") == "5000"
    assert normalizer("one hundred zero") == "1000"
