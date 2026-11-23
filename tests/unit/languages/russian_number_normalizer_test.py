import pytest

from normalization.languages.russian.number_normalizer import RussianNumberNormalizer


@pytest.fixture
def normalizer() -> RussianNumberNormalizer:
    return RussianNumberNormalizer()


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("двадцать пять", "25"),
        ("Двадцать пять", "25"),
        ("двадцати пяти", "25"),
        ("двадцать один", "21"),
        ("сто одна", "101"),
        ("две тысячи двадцать пять", "2025"),
        ("один миллион", "1000000"),
        ("ноль", "0"),
        ("шесть целых пять десятых", "6,5"),
        ("Он сказал: двадцать пять, а не тридцать.", "Он сказал: 25, а не 30."),
    ],
)
def test_cardinals(normalizer: RussianNumberNormalizer, text: str, expected: str):
    assert normalizer(text) == expected


@pytest.mark.parametrize(
    "text",
    [
        "один из них",
        "он один",
        "одну минуту",
        "с одной стороны",
        "полторы тысячи",
        "полтора миллиона",
        # Ordinals are left as words.
        "двадцать первый век",
        "в двадцатом веке",
        # Homographs of oblique number forms.
        "сорока на ветке",
        "всей семью",
    ],
)
def test_left_as_words(normalizer: RussianNumberNormalizer, text: str):
    assert normalizer(text) == text


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("пять километров", "5 км"),
        ("1 километр", "1 км"),
        ("в 5 километрах", "в 5 км"),
        ("2 метра", "2 м"),
        ("10 сантиметров", "10 см"),
        ("три килограмма", "3 кг"),
        ("в 2025 году", "в 2025 г"),
        ("с 1999 года", "с 1999 г"),
        ("пять процентов", "5 процентов"),
        ("двадцать один процент", "21 процентов"),
        ("два процента", "2 процентов"),
    ],
)
def test_words_after_a_number_are_folded(
    normalizer: RussianNumberNormalizer, text: str, expected: str
):
    assert normalizer(text) == expected


@pytest.mark.parametrize(
    "text",
    [
        "сколько километров",
        "новый год",
        "5 лет",
        "процент от суммы",
        "5-километровый",
    ],
)
def test_words_without_a_number_are_not_folded(
    normalizer: RussianNumberNormalizer, text: str
):
    assert normalizer(text) == text


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("5 млн", "5000000"),
        ("5 млн.", "5000000"),
        ("5 миллионов", "5000000"),
        ("2 тыс. человек", "2000 человек"),
        ("2 тысячи человек", "2000 человек"),
        ("3 млрд", "3000000000"),
        # "тыс." before an era is a millennium, not a thousand.
        ("3 тыс. до н. э.", "3 тыс. до нашей эры"),
        ("3 тысячелетие", "3 тысячелетие"),
        # A number word after the scale: kept apart, never merged into 2000500.
        ("2 тысячи пятьсот", "2 тысячи 500"),
    ],
)
def test_scales_after_an_integer(
    normalizer: RussianNumberNormalizer, text: str, expected: str
):
    assert normalizer(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("в 79 году н. э.", "в 79 г нашей эры"),
        ("в 79 г. н. э.", "в 79 г. нашей эры"),
        ("в 79 н.э.", "в 79 нашей эры"),
        ("до н. э.", "до нашей эры"),
        ("в I в. н. э.", "в I в. нашей эры"),
        # Initials, not an era: nothing before them is a year, a century or "до".
        ("им. Н. Э. Баумана", "им. Н. Э. Баумана"),
    ],
)
def test_era(normalizer: RussianNumberNormalizer, text: str, expected: str):
    assert normalizer(text) == expected
