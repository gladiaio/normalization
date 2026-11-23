"""gladia-3 scores the script variants of one Japanese word the same (#58)."""

import pytest

from normalization import load_pipeline


@pytest.fixture(scope="module")
def ja():
    return load_pipeline("gladia-3", "ja")


@pytest.mark.parametrize(
    "forms",
    [
        ("コロコロ", "ころころ"),
        ("人々", "人人"),
        ("コンピューター", "コンピュータ"),
        ("3ヶ月", "3ヵ月", "3か月"),
        ("ヴァイオリン", "ゔぁいおりん"),
    ],
)
def test_variants_are_equal(ja, forms: tuple[str, ...]) -> None:
    assert len({ja.normalize(form) for form in forms}) == 1


@pytest.mark.parametrize(
    ("a", "b"),
    [("鳴った", "なった"), ("箸", "橋"), ("ハード", "ハド"), ("ビザ", "ヒサ")],
)
def test_different_words_stay_different(ja, a: str, b: str) -> None:
    assert ja.normalize(a) != ja.normalize(b)


def test_other_languages_keep_katakana() -> None:
    assert load_pipeline("gladia-3", "en").normalize("コロコロ") == "コロコロ"
