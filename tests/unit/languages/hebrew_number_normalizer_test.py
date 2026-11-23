import pytest

from normalization.languages.hebrew.number_normalizer import HebrewNumberNormalizer


@pytest.fixture(scope="module")
def normalizer() -> HebrewNumberNormalizer:
    return HebrewNumberNormalizer()


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("אפס", "0"),
        # Feminine and masculine units.
        ("שתיים", "2"),
        ("שניים", "2"),
        ("שלוש", "3"),
        ("שלושה", "3"),
        ("חמש", "5"),
        ("חמישה", "5"),
        ("שמונה", "8"),
        ("עשר", "10"),
        ("עשרה", "10"),
        # Teens, both genders.
        ("אחת עשרה", "11"),
        ("אחד עשר", "11"),
        ("שתים עשרה", "12"),
        ("שנים עשר", "12"),
        ("חמש עשרה", "15"),
        ("חמישה עשר", "15"),
        ("שמונה עשרה", "18"),
        ("שתים-עשרה", "12"),
        ("שתים־עשרה", "12"),
        # Tens and the conjunction before the last element.
        ("עשרים", "20"),
        ("עשרים וחמש", "25"),
        ("עשרים וחמישה", "25"),
        ("עשרים ואחד", "21"),
        ("שמונים ושניים", "82"),
        # Hundreds.
        ("מאה", "100"),
        ("מאתיים", "200"),
        ("שלוש מאות", "300"),
        ("מאה ועשרים", "120"),
        ("מאה עשרים ושלוש", "123"),
        # Thousands.
        ("אלף", "1000"),
        ("אלפיים", "2000"),
        ("שלושת אלפים", "3000"),
        ("עשרת אלפים", "10000"),
        ("ששת אלפי דירות", "6000 דירות"),
        ("עשרים וחמישה אלף", "25000"),
        ("אלף תשע מאות שמונים וארבע", "1984"),
        ("אלפיים ועשרים וחמש", "2025"),
        ("חמשת אלפים שש מאות חמישים ושלוש", "5653"),
        ("חמישה עשר אלף שבע מאות שלושים וחמישה", "15735"),
        ("תשעים ותשעה אלף ארבע מאות", "99400"),
        # Millions.
        ("מיליון", "1000000"),
        ("שני מיליון נשים", "2000000 נשים"),
        ("שלושה מיליון צפיות", "3000000 צפיות"),
        # In a sentence.
        ("היו שם עשרים וחמישה אנשים", "היו שם 25 אנשים"),
        ("שלוש מאות ילדים", "300 ילדים"),
    ],
)
def test_cardinals(normalizer: HebrewNumberNormalizer, text: str, expected: str):
    assert normalizer(text) == expected


@pytest.mark.parametrize(
    "text",
    [
        # "one" alone is a pronoun or a determiner.
        "אחד",
        "אחת",
        "מישהו אחד",
        # Construct forms quantify a definite noun, or are another word.
        "שלושת הילדים",
        "שני הספרים",
        "יום שני",
        # "שנים" means "years" outside a teen.
        "לפני שנים רבות",
        "שתים",
        "בית ספר",
        "",
    ],
)
def test_words_left_as_written(normalizer: HebrewNumberNormalizer, text: str):
    assert normalizer(text) == text


def test_conjunction_before_the_first_element_is_kept(
    normalizer: HebrewNumberNormalizer,
):
    assert normalizer("שלושה ושלושה") == "3 ו-3"


def test_punctuation_ends_a_number(normalizer: HebrewNumberNormalizer):
    assert normalizer("עשרים, חמש") == "20, 5"
    assert normalizer('אמר: "שלוש"') == 'אמר: "3"'


def test_two_units_do_not_merge(normalizer: HebrewNumberNormalizer):
    assert normalizer("שלוש ארבע") == "3 4"
