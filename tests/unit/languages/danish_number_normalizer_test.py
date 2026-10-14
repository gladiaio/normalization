import pytest

from normalization.languages.danish.number_normalizer import DanishNumberNormalizer
from normalization.languages.danish.operators import DANISH_CONFIG


@pytest.fixture
def normalizer() -> DanishNumberNormalizer:
    return DanishNumberNormalizer(DANISH_CONFIG.currency_symbol_to_word)


@pytest.fixture
def normalizer_no_currency() -> DanishNumberNormalizer:
    return DanishNumberNormalizer(None)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        # Basic digits and teens
        ("ni", "9"),
        ("elleve", "11"),
        ("femten", "15"),
        ("nitten", "19"),
        # Vigesimal tens (unique to Danish)
        ("tyve", "20"),
        ("tredive", "30"),
        ("tredve", "30"),  # colloquial variant
        ("fyrre", "40"),
        ("halvtreds", "50"),
        ("tres", "60"),
        ("halvfjerds", "70"),
        ("firs", "80"),
        ("halvfems", "90"),
        # Three-word og-compounds
        ("en og tyve", "21"),
        ("to og tyve", "22"),
        ("tre og halvtreds", "53"),
        ("ni og halvfems", "99"),
        ("fem og firs", "85"),
        # Glued og-compounds
        ("enogtyve", "21"),
        ("etogtyve", "21"),  # neuter-"et" glued form
        ("toogtyve", "22"),
        ("fireogfirs", "84"),
        ("nioghalvfems", "99"),
        ("treoghalvfjerds", "73"),
        # Hundreds
        ("hundrede", "100"),
        ("to hundrede", "200"),
        ("ni hundrede", "900"),
        ("to hundrede og en", "201"),
        ("tre hundrede og femten", "315"),
        ("to hundrede og en og tyve", "221"),
        ("to hundrede og fireoghalvtreds", "254"),
        # Tusind
        ("tusind", "1000"),
        ("et tusind", "1000"),
        ("en tusind", "1000"),  # common-gender form
        ("to tusind", "2000"),
        ("to tusind tre hundrede", "2300"),
        ("tres tusind", "60000"),
        # Large multipliers
        ("en million", "1000000"),
        ("to millioner", "2000000"),
        ("en milliard", "1000000000"),
        ("to milliarder", "2000000000"),
        ("en billion", "1000000000000"),
        ("to billioner", "2000000000000"),
        # Mixed digit + word
        ("3 milliard", "3000000000"),
        ("5 million", "5000000"),
        # Zero
        ("nul", "0"),
    ],
)
def test_danish_spelled_numbers(
    normalizer: DanishNumberNormalizer, text: str, expected: str
) -> None:
    assert normalizer(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("ti euro", "10 euro"),
        ("hundrede kroner", "100 kroner"),
        ("€10", "10 euro"),
        ("10 kr", "10 kroner"),
        ("£50", "50 pund"),
        ("fem dollar", "5 dollar"),
    ],
)
def test_currency_symbols_and_plural_trailing_words(
    normalizer: DanishNumberNormalizer, text: str, expected: str
) -> None:
    assert normalizer(text) == expected


def test_without_currency_config_leaves_currency_symbol(
    normalizer_no_currency: DanishNumberNormalizer,
) -> None:
    assert normalizer_no_currency("en og tyve") == "21"
    assert normalizer_no_currency("€10") == "€10"
    assert normalizer_no_currency("3 milliard") == "3000000000"


def test_non_numeric_text_unchanged(normalizer: DanishNumberNormalizer) -> None:
    text = "det her er almindelig tekst"
    assert normalizer(text) == text


def test_kroner_word_not_treated_as_currency_suffix(
    normalizer: DanishNumberNormalizer,
) -> None:
    assert normalizer("25 kroner") == "25 kroner"


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        # Simple ordinals (standalone)
        ("første", "1."),
        ("anden", "2."),
        ("tredje", "3."),
        ("tiende", "10."),
        ("tyvende", "20."),
        # Glued og-compound ordinals (e.g. "enogtyvende" = 21st)
        ("enogtyvende", "21."),
        ("toogtyvende", "22."),
        ("fireogfyrrende", "44."),
        # Cardinal + ordinal suffix (e.g. "hundrede tyvende" = 120th)
        ("hundrede tyvende", "120."),
        ("hundrede enogtyvende", "121."),
    ],
)
def test_danish_ordinals(
    normalizer: DanishNumberNormalizer, text: str, expected: str
) -> None:
    assert normalizer(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        # "tusinde" (with -e) should be treated the same as "tusind"
        ("tusinde", "1000"),
        ("et tusinde", "1000"),
        ("to tusinde", "2000"),
        ("to tusinde tre hundrede", "2300"),
        ("to tusinde fem og tyve", "2025"),
    ],
)
def test_tusinde_variant(
    normalizer: DanishNumberNormalizer, text: str, expected: str
) -> None:
    assert normalizer(text) == expected
