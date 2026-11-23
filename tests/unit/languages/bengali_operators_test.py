import pytest

from normalization import load_pipeline
from normalization.languages.bengali import BengaliOperators
from normalization.languages.registry import get_language_registry


@pytest.fixture
def operators() -> BengaliOperators:
    return BengaliOperators()


def test_bengali_is_registered() -> None:
    assert isinstance(get_language_registry()["bn"](), BengaliOperators)


def test_config_code(operators: BengaliOperators) -> None:
    assert operators.config.code == "bn"


def test_bengali_digits_become_ascii(operators: BengaliOperators) -> None:
    table = str.maketrans(operators.config.character_replacements or {})
    assert "০১২৩৪৫৬৭৮৯".translate(table) == "0123456789"


@pytest.mark.parametrize(
    ("conjunct", "anusvara"),
    [("অহঙ্কারী", "অহংকারী"), ("সঙ্গীত", "সংগীত"), ("ভয়ঙ্কর", "ভয়ংকর"), ("অঙ্ক", "অংক")],
)
def test_velar_nasal_conjunct_is_anusvara(
    operators: BengaliOperators, conjunct: str, anusvara: str
) -> None:
    assert operators.normalize_spelling_variants(conjunct) == anusvara
    pipeline = load_pipeline("gladia-3", "bn")
    assert pipeline.normalize(conjunct) == pipeline.normalize(anusvara)


@pytest.mark.parametrize("word", ["বাংলা", "কান্না", "অন্য", "সম্মান", "পড়া", "বাঁশ"])
def test_other_nasals_and_signs_are_kept(
    operators: BengaliOperators, word: str
) -> None:
    """Only ঙ before a velar is folded; chandrabindu and nukta letters are not."""
    assert operators.normalize_spelling_variants(word) == word


def test_chandrabindu_is_not_folded() -> None:
    pipeline = load_pipeline("gladia-3", "bn")
    assert pipeline.normalize("বাঁশ") != pipeline.normalize("বাংশ")


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("পঁচিশ", "25"),
        ("২৫", "25"),
        ("দুই হাজার বিশ", "2020"),
        ("তিনশো পঞ্চাশ", "350"),
        ("তিনশত পঞ্চাশ", "350"),
        ("তিন শো টাকা", "300 টাকা"),
        ("দুশো", "200"),
        ("তৃতীয়", "3য়"),
        # "দশ" is ten; "তিনি" ("he", "she") is not "তিন" ("three").
        ("তিনি এসেছেন", "তিনি এসেছেন"),
        ("আমি এক কাপ চা খাব", "আমি এক কাপ চা খাব"),
    ],
)
def test_numbers(text: str, expected: str) -> None:
    assert load_pipeline("gladia-3", "bn").normalize(text) == expected
