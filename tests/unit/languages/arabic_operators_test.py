import pytest

from normalization.languages.arabic.operators import ArabicOperators
from normalization.languages.registry import get_language_registry
from normalization.pipeline.loader import load_pipeline


@pytest.fixture
def operators() -> ArabicOperators:
    return ArabicOperators()


@pytest.fixture(scope="module")
def pipeline():
    return load_pipeline("gladia-3", "ar")


def test_arabic_is_registered() -> None:
    assert "ar" in get_language_registry()


def test_arabic_registry_produces_arabic_operators() -> None:
    instance = get_language_registry()["ar"]()
    assert isinstance(instance, ArabicOperators)


def test_config_code(operators: ArabicOperators) -> None:
    assert operators.config.code == "ar"


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("يكلف $50", "يكلف 50 دولار"),
        ("20%", "20 بالميه"),
        ("12.5", "12 فاصله 5"),
        ("امم نعم", "نعم"),
    ],
)
def test_pipeline_symbols_and_fillers(pipeline, text: str, expected: str) -> None:
    assert pipeline.normalize(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("مَرْحَبًا بِكُمْ", "مرحبا بكم"),
        ("مُحَمَّدٌ", "محمد"),
        ("هٰذا", "هذا"),
        ("عـــربي", "عربي"),
    ],
)
def test_pipeline_strips_harakat_and_tatweel(
    pipeline, text: str, expected: str
) -> None:
    assert pipeline.normalize(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("أنا ذهبت إلى المدرسة", "انا ذهبت الي المدرسه"),
        ("آمن", "امن"),
        ("ٱلله", "الله"),
        ("مستشفى", "مستشفي"),
        ("مستشفي", "مستشفي"),
        ("کتاب عربی", "كتاب عربي"),
    ],
)
def test_pipeline_unifies_letter_variants(pipeline, text: str, expected: str) -> None:
    assert pipeline.normalize(text) == expected
