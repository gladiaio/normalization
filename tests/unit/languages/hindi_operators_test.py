"""Hindi spelling folds follow the standard orthography of the Central Hindi Directorate
(देवनागरी लिपि एवं हिंदी वर्तनी का मानकीकरण, 2024), cited by rule number."""

import pytest

from normalization import load_pipeline
from normalization.languages.hindi import HINDI_REPLACEMENTS, HindiOperators
from normalization.languages.registry import get_language_registry


@pytest.fixture
def operators() -> HindiOperators:
    return HindiOperators()


def test_hindi_is_registered() -> None:
    assert isinstance(get_language_registry()["hi"](), HindiOperators)


def test_config_code(operators: HindiOperators) -> None:
    assert operators.config.code == "hi"


def test_devanagari_digits_become_ascii(operators: HindiOperators) -> None:
    table = str.maketrans(operators.config.character_replacements or {})
    assert "०१२३४५६७८९".translate(table) == "0123456789"


@pytest.mark.parametrize(
    ("with_nukta", "without"),
    [
        ("ज़मीन", "जमीन"),
        ("टेलीविज़न", "टेलीविजन"),
        ("फ़्री", "फ्री"),
        ("ख़बर", "खबर"),
        ("क़लम", "कलम"),
        ("ग़लत", "गलत"),
        # Decomposed: base letter + U+093C
        ("ज़मीन", "जमीन"),
    ],
)
def test_urdu_nukta_is_folded(with_nukta: str, without: str) -> None:
    """Rule 3.15.1: Urdu words absorbed by Hindi are written without the nukta."""
    pipeline = load_pipeline("gladia-3", "hi")
    assert pipeline.normalize(with_nukta) == pipeline.normalize(without) == without


@pytest.mark.parametrize("word", ["पढ़ा", "सड़क", "पढ़ा"])
def test_nukta_of_hindi_letters_is_kept(word: str) -> None:
    """ड़ and ढ़ are letters of the Hindi alphabet, not Urdu sounds."""
    pipeline = load_pipeline("gladia-3", "hi")
    assert pipeline.normalize(word) != pipeline.normalize(
        word.replace("़", "").replace("ड़", "ड").replace("ढ़", "ढ")
    )


@pytest.mark.parametrize(
    ("conjunct", "anusvara"),
    [
        ("केन्द्रीय", "केंद्रीय"),
        ("भूकम्प", "भूकंप"),
        ("गङ्गा", "गंगा"),
        ("चञ्चल", "चंचल"),
        ("पण्डित", "पंडित"),
        ("सम्बन्ध", "संबंध"),
    ],
)
def test_nasal_conjunct_of_its_own_class_is_anusvara(
    operators: HindiOperators, conjunct: str, anusvara: str
) -> None:
    """Rule 3.6.1.2 and 3.6.2.5 (क)."""
    assert operators.normalize_spelling_variants(conjunct) == anusvara


@pytest.mark.parametrize("word", ["अन्य", "उन्मुख", "चिन्मय", "अन्न", "सम्मेलन", "सम्मति"])
def test_nasal_conjunct_of_another_class_or_doubled_is_kept(
    operators: HindiOperators, word: str
) -> None:
    """Rules 3.6.1.3 and 3.6.1.4."""
    assert operators.normalize_spelling_variants(word) == word


@pytest.mark.parametrize(
    ("chandrabindu", "anusvara"),
    [("चाँद", "चांद"), ("यहाँ", "यहां"), ("महिलाएँ", "महिलाएं"), ("पाँच", "पांच")],
)
def test_chandrabindu_is_folded_into_anusvara(
    operators: HindiOperators, chandrabindu: str, anusvara: str
) -> None:
    """Rule 3.6.2.5: anusvara is written for chandrabindu in newspapers and textbooks."""
    assert operators.normalize_spelling_variants(chandrabindu) == anusvara


@pytest.mark.parametrize(
    ("chandrabindu", "anusvara"),
    [("हँस", "हंस"), ("हँसना", "हंसना"), ("अँगना", "अंगना")],
)
def test_chandrabindu_minimal_pairs_stay_apart(
    chandrabindu: str, anusvara: str
) -> None:
    """Rule 3.6.2.3: हंस "swan" / हँस "laugh" and अंगना / अँगना are different words."""
    pipeline = load_pipeline("gladia-3", "hi")
    assert pipeline.normalize(chandrabindu) != pipeline.normalize(anusvara)


@pytest.mark.parametrize(
    ("glide", "vowel"),
    [
        ("गये", "गए"),
        ("गयी", "गई"),
        ("आये", "आए"),
        ("किये", "किए"),
        ("चाहिये", "चाहिए"),
        ("किराये", "किराए"),
    ],
)
def test_glide_ya_is_folded_to_the_vowel(glide: str, vowel: str) -> None:
    """Rule 3.14.1: गया - गई - गए."""
    assert HINDI_REPLACEMENTS[glide] == vowel
    pipeline = load_pipeline("gladia-3", "hi")
    assert pipeline.normalize(glide) == pipeline.normalize(vowel) == vowel


@pytest.mark.parametrize(
    ("a", "b"),
    [
        ("गायें", "गाएं"),  # "cows" / "may sing"
        ("दिये", "दिए"),  # "lamps" / "gave"
        ("ये", "ए"),  # "these" / the vowel
    ],
)
def test_glide_ya_is_not_a_general_rule(a: str, b: str) -> None:
    pipeline = load_pipeline("gladia-3", "hi")
    assert pipeline.normalize(a) != pipeline.normalize(b)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("पच्चीस", "25"),
        ("तीन सौ पचास", "350"),
        ("दो हज़ार बीस", "2020"),
        ("पाँच सौ रुपये", "500 रुपए"),
        ("वह तीसरा था", "वह 3रा था"),
        ("२५", "25"),
        # A lone "एक" stays a word, like English "one".
        ("एक बार की बात है", "एक बार की बात है"),
    ],
)
def test_numbers(text: str, expected: str) -> None:
    assert load_pipeline("gladia-3", "hi").normalize(text) == expected
