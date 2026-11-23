import pytest

from normalization.languages.japanese.number_normalizer import JapaneseNumberNormalizer


@pytest.fixture
def normalizer() -> JapaneseNumberNormalizer:
    return JapaneseNumberNormalizer()


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("二十五メートル", "25メートル"),
        ("三月十五日", "3月15日"),
        ("二十五", "25"),
        ("一億二千六百四十四万三千人", "126443000人"),
        ("午後二時三十七分", "午後2時37分"),
        ("第一部", "第1部"),
        ("一番目", "1番目"),
    ],
)
def test_kanji_numerals_are_read(
    normalizer: JapaneseNumberNormalizer, text: str, expected: str
) -> None:
    assert normalizer(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("1万2千", "12000"),
        ("１万２千", "12000"),
        ("1万二千", "12000"),
        ("30万円", "300000円"),
        ("2千円", "2000円"),
        ("1億2644万3000人", "126443000人"),
        ("約30万人が参加した", "約300000人が参加した"),
    ],
)
def test_digits_mixed_with_units_keep_their_value(
    normalizer: JapaneseNumberNormalizer, text: str, expected: str
) -> None:
    assert normalizer(text) == expected


def test_mixed_form_equals_kanji_form(normalizer: JapaneseNumberNormalizer) -> None:
    assert normalizer("30万円") == normalizer("三十万円") == "300000円"
    assert normalizer("1万2千") == normalizer("一万二千")


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("二〇二五年", "2025年"),
        ("一〇〇", "100"),
        ("約一・五倍", "約1.5倍"),
    ],
)
def test_positional_digits_and_kanji_decimals(
    normalizer: JapaneseNumberNormalizer, text: str, expected: str
) -> None:
    assert normalizer(text) == expected


def test_range_without_zero_is_not_positional(
    normalizer: JapaneseNumberNormalizer,
) -> None:
    # 三四人 is "three or four people", not 34.
    assert normalizer("三四人") == "三四人"


@pytest.mark.parametrize(
    ("text", "expected"),
    [("一つ", "1つ"), ("二つ", "2つ"), ("一人", "1人"), ("一日", "1日")],
)
def test_counting_forms_use_digits(
    normalizer: JapaneseNumberNormalizer, text: str, expected: str
) -> None:
    assert normalizer(text) == expected


@pytest.mark.parametrize(
    "text",
    [
        # Idioms, set phrases and words built with a numeral (公用文作成の考え方 I-4 カ)
        "千里の道も一歩から",
        "三日坊主",
        "二十四節気",
        "四十九日",
        "七五三",
        # Dictionary words words2num2 alone would read
        "一部の人",
        "一層",
        "一番大きい",
        "万一の場合",
        "万が一",
        "三日月",
        "八百屋さん",
        "十八番",
        "五分五分",
        "五月雨",
        "八十八夜",
        "百人一首",
        "八つ当たり",
        "十人十色",
        "万歳",
        "万年筆",
        "三角形",
        # Words words2num2 already keeps
        "一緒に",
        "統一",
        "唯一",
        "十分",
        "一般",
        "一生",
        "一方",
        # Approximate numbers (I-4 オ)
        "数十人",
        "何百回",
        "幾千",
    ],
)
def test_words_with_a_numeral_keep_their_kanji(
    normalizer: JapaneseNumberNormalizer, text: str
) -> None:
    assert normalizer(text) == text


def test_kept_word_inside_a_sentence(normalizer: JapaneseNumberNormalizer) -> None:
    assert normalizer("一緒に二十五個買った") == "一緒に25個買った"
    assert normalizer("一部の二十人") == "一部の20人"


def test_empty_text(normalizer: JapaneseNumberNormalizer) -> None:
    assert normalizer("") == ""
    assert normalizer("  ") == "  "
