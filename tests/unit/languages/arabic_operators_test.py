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


def test_config_words_are_in_normalized_form(operators: ArabicOperators) -> None:
    config = operators.config
    assert config.character_replacements is not None
    assert config.decimal_word is not None
    folded = {k for k, v in config.character_replacements.items() if k != v}
    words = [
        *config.symbols_to_words.values(),
        *config.currency_symbol_to_word.values(),
        *config.filler_words,
        *(config.digit_words or {}),
        config.decimal_word,
    ]
    for word in words:
        assert not folded & set(word), word


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("يكلف $50", "يكلف 50 دولار"),
        ("20%", "20 بالميه"),
        ("12.5", "12 فاصله 5"),
        ("اممم نعم", "نعم"),
    ],
)
def test_pipeline_symbols_and_fillers(pipeline, text: str, expected: str) -> None:
    assert pipeline.normalize(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("أمم كثيرة", "امم كثيره"),
        ("اه والله", "اه والله"),
    ],
)
def test_pipeline_keeps_real_words_that_look_like_fillers(
    pipeline, text: str, expected: str
) -> None:
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
        ("سؤال", "سوال"),
        ("رئيس", "رييس"),
    ],
)
def test_pipeline_unifies_letter_variants(pipeline, text: str, expected: str) -> None:
    assert pipeline.normalize(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("عندي ٣ كتب", "عندي 3 كتب"),
        ("۱۲۳", "123"),
        ("١٢٫٥ كيلو", "12 فاصله 5 كيلو"),
        ("١٬٠٠٠ دولار", "1000 دولار"),
        ("٢٠٪", "20 بالميه"),
    ],
)
def test_pipeline_converts_native_digits_and_separators(
    pipeline, text: str, expected: str
) -> None:
    assert pipeline.normalize(text) == expected


@pytest.mark.parametrize(
    ("words", "digits"),
    [
        ("عندي خمسة وعشرون كتاباً", "عندي ٢٥ كتاباً"),
        ("سنة ألفين وخمسة وعشرين", "سنة ٢٠٢٥"),
        ("ثلاثة فاصلة خمسة", "٣٫٥"),
        ("عشرون بالمئة", "٢٠٪"),
        ("ثلاثة آلاف دولار", "٣٬٠٠٠ دولار"),
        ("ثلاثة وأربعة", "٣ و٤"),
        ("مئة وخمسة وعشرون", "١٢٥"),
    ],
)
def test_pipeline_spelled_out_numbers_match_digits(
    pipeline, words: str, digits: str
) -> None:
    assert pipeline.normalize(words) == pipeline.normalize(digits)


def test_pipeline_collapses_digit_word_sequences(pipeline) -> None:
    assert pipeline.normalize("واحد اثنين ثلاثة أربعة") == "1234"


# --- #68: format characters and hamza seats ---


@pytest.mark.parametrize(
    "marked",
    [
        "‏مرحبا",  # RLM
        "مرحبا‎",  # LRM
        "؜مرحبا",  # Arabic letter mark
        "⁨مرحبا⁩",  # first strong isolate ... pop directional isolate
        "﻿مرحبا",  # BOM / zero width no-break space
        "‫مرحبا‬",  # right-to-left embedding ... pop directional formatting
        "مرحبا۝",  # end of ayah
    ],
)
def test_format_characters_removed(pipeline, marked: str) -> None:
    assert pipeline.normalize(marked) == pipeline.normalize("مرحبا")


def test_zero_width_space_is_not_a_word_break(pipeline) -> None:
    assert pipeline.normalize("مرحبا​بك") == pipeline.normalize("مرحبابك")


@pytest.mark.parametrize(
    ("waw_seat", "other_seat"),
    [
        ("مسؤول", "مسئول"),
        ("شؤون", "شئون"),
        ("رؤوس", "رءوس"),
        ("يقرؤون", "يقرءون"),
    ],
)
def test_hamza_seat_before_waw_folded(pipeline, waw_seat: str, other_seat: str) -> None:
    assert pipeline.normalize(waw_seat) == pipeline.normalize(other_seat)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("بيئة", "بييه"),  # ئ before another letter: plain ئ → ي
        ("هيئة", "هييه"),
        ("سماء", "سماء"),  # word-final ء untouched
        ("سؤال", "سوال"),  # ؤ before another letter: plain ؤ → و
        ("رئيس", "رييس"),
    ],
)
def test_hamza_seat_elsewhere_unchanged(pipeline, text: str, expected: str) -> None:
    assert pipeline.normalize(text) == expected


def test_spelling_variants_leave_other_text_alone(operators: ArabicOperators) -> None:
    assert operators.normalize_spelling_variants("hello 123") == "hello 123"


def test_numbers_with_hamza_still_read(pipeline) -> None:
    assert pipeline.normalize("ثلاثمئة وخمسة") == "305"
    assert pipeline.normalize("مئتين") == "200"
