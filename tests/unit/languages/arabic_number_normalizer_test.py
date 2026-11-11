import pytest

from normalization.languages.arabic.number_normalizer import ArabicNumberNormalizer
from normalization.languages.arabic.operators import ARABIC_CONFIG


@pytest.fixture(scope="module")
def normalizer() -> ArabicNumberNormalizer:
    return ArabicNumberNormalizer(ARABIC_CONFIG.character_replacements)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("صفر", "0"),
        ("اثنان", "2"),
        ("اثنين", "2"),
        ("ثلاثة", "3"),
        ("ثلاث", "3"),
        ("أربعة", "4"),
        ("خمسة", "5"),
        ("ستة", "6"),
        ("سبعة", "7"),
        ("ثمانية", "8"),
        ("ثماني", "8"),
        ("تسعة", "9"),
        ("عشرة", "10"),
        ("عشر", "10"),
    ],
)
def test_units(normalizer: ArabicNumberNormalizer, text: str, expected: str) -> None:
    assert normalizer(text) == expected


@pytest.mark.parametrize(
    "text",
    ["واحد", "واحدة", "أحد", "إحدى", "ولد واحد", "يوم الأحد"],
)
def test_standalone_one_is_kept_as_a_word(
    normalizer: ArabicNumberNormalizer, text: str
) -> None:
    # Like English "one", these double as pronouns ("someone", "one of").
    assert normalizer(text) == text


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("أحد عشر", "11"),
        ("إحدى عشرة", "11"),
        ("اثنا عشر", "12"),
        ("اثني عشر", "12"),
        ("اثنتا عشرة", "12"),
        ("ثلاثة عشر", "13"),
        ("خمس عشرة", "15"),
        ("تسعة عشر", "19"),
    ],
)
def test_teens(normalizer: ArabicNumberNormalizer, text: str, expected: str) -> None:
    assert normalizer(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("عشرون", "20"),
        ("عشرين", "20"),
        ("ثلاثون", "30"),
        ("أربعين", "40"),
        ("تسعون", "90"),
        ("واحد وعشرون", "21"),
        ("خمسة وعشرون", "25"),
        ("خمسة و عشرين", "25"),
        ("ثلاثة وتسعين", "93"),
    ],
)
def test_tens_and_compounds(
    normalizer: ArabicNumberNormalizer, text: str, expected: str
) -> None:
    assert normalizer(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("مئة", "100"),
        ("مائة", "100"),
        ("مية", "100"),
        ("مئتان", "200"),
        ("مئتين", "200"),
        ("ثلاثمئة", "300"),
        ("ثلاثمائة", "300"),
        ("ثلاث مئة", "300"),
        ("خمسمية", "500"),
        ("تسعمائة", "900"),
        ("مئة وخمسة", "105"),
        ("مئة وواحد", "101"),
        ("مئة وخمسة وعشرون", "125"),
        ("ثلاثمئة وأحد عشر", "311"),
    ],
)
def test_hundreds(normalizer: ArabicNumberNormalizer, text: str, expected: str) -> None:
    assert normalizer(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("ألف", "1000"),
        ("ألفان", "2000"),
        ("ألفين", "2000"),
        ("ثلاثة آلاف", "3000"),
        ("عشرة آلاف", "10000"),
        ("أحد عشر ألفاً", "11000"),
        ("خمسة وعشرين ألف", "25000"),
        ("مئة ألف", "100000"),
        ("ألف وتسعمائة وتسعين", "1990"),
        ("ألفين وخمسة وعشرين", "2025"),
        ("ثلاثة آلاف وخمسمائة", "3500"),
        ("مليون", "1000000"),
        ("مليونين", "2000000"),
        ("ثلاثة ملايين", "3000000"),
        ("ثلاثة ملايين وخمسمائة ألف", "3500000"),
        ("مليار", "1000000000"),
        ("خمسة مليارات", "5000000000"),
    ],
)
def test_thousands_and_above(
    normalizer: ArabicNumberNormalizer, text: str, expected: str
) -> None:
    assert normalizer(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("3 آلاف", "3000"),
        ("٥ ملايين", "5000000"),
        ("25 ألف", "25000"),
    ],
)
def test_digits_followed_by_a_scale_word(
    normalizer: ArabicNumberNormalizer, text: str, expected: str
) -> None:
    assert normalizer(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("اتنين", "2"),
        ("تلاتة", "3"),
        ("تمانية", "8"),
        ("حداشر", "11"),
        ("اتناشر", "12"),
        ("خمستاشر", "15"),
        ("تلاتين", "30"),
        ("تلتمية", "300"),
        ("ميتين", "200"),
        ("تلات تلاف", "3000"),
    ],
)
def test_dialect_spellings(
    normalizer: ArabicNumberNormalizer, text: str, expected: str
) -> None:
    assert normalizer(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        # "و" only joins a unit to a tens word or a smaller group to a larger
        # one; anything else is the plain conjunction "and".
        ("ثلاثة وأربعة", "3 و4"),
        ("عشرين وخمسة", "20 و5"),
        ("و خمسة", "و 5"),
        ("عندي خمسة وعشرون كتاب", "عندي 25 كتاب"),
        ("سنة ألفين وعشرين", "سنة 2020"),
        ("خمسة، ستة", "5، 6"),
        ("الساعة ثلاثة", "الساعة 3"),
        ("ثلاثة فاصلة خمسة", "3 فاصلة 5"),
        ("عشرين بالمئة", "20 بالمئة"),
        ("من غير أرقام", "من غير أرقام"),
        ("", ""),
    ],
)
def test_numbers_in_context(
    normalizer: ArabicNumberNormalizer, text: str, expected: str
) -> None:
    assert normalizer(text) == expected
