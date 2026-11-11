import pytest

from normalization.languages.romanian.number_normalizer import RomanianNumberNormalizer


@pytest.fixture
def normalizer() -> RomanianNumberNormalizer:
    return RomanianNumberNormalizer()


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        # Units, teens, tens
        ("zero", "0"),
        ("nouă", "9"),
        ("zece", "10"),
        ("unsprezece", "11"),
        ("nouăsprezece", "19"),
        ("douăzeci", "20"),
        ("nouăzeci", "90"),
        # Standard and informal teens (everyday speech contracts them)
        ("cincisprezece", "15"),
        ("cincișpe", "15"),
        ("cinșpe", "15"),  # the most reduced form
        ("unșpe", "11"),
        ("doișpe", "12"),
        ("douășpe", "12"),  # feminine: "e ora douășpe"
        ("patrușcinci", "45"),  # fused "patruzeci și cinci"
        ("patrușcinci de lei", "45 lei"),
        ("șaișpe", "16"),
        ("douăj", "20"),
        # Compounds with "și", also written as one word
        ("douăzeci și cinci", "25"),
        ("nouăzeci și nouă", "99"),
        ("douăzecișicinci", "25"),
        ("Douăzecişicinci", "25"),
        # Hundreds
        ("o sută", "100"),
        ("trei sute cincizeci și doi", "352"),
        # Multipliers, with the "de" used from 20 up
        ("o mie", "1000"),
        ("două mii", "2000"),
        ("douăzeci de mii", "20000"),
        ("o sută de mii", "100000"),
        ("două milioane cinci sute de mii", "2500000"),
        ("un miliard", "1000000000"),
        # Without diacritics, and with the legacy cedilla letters
        ("douazeci si cinci", "25"),
        ("şase", "6"),
        ("şaptezeci", "70"),
        # The "de" linking a number of 20+ (or ending in 00) to its noun is dropped,
        # so spoken and written forms agree
        ("douăzeci de grade", "20 grade"),
        ("20 de grade", "20 grade"),
        ("douăzeci și cinci de lei", "25 lei"),
        ("am plătit trei sute de lei", "am plătit 300 lei"),
        ("o sută de lei", "100 lei"),
        ("douăzeci de mii de oameni", "20000 oameni"),
        # ...but not after smaller numbers, nor in "de la" ("from")
        ("cinci grade", "5 grade"),
        ("doi de la tine", "2 de la tine"),
        ("douăzeci de la bunica", "20 de la bunica"),
        # Punctuation and a unit after a unit start new numbers
        ("zece, unsprezece", "10, 11"),
        ("doi trei oameni", "2 3 oameni"),
        # Ordinals after "al"/"a", spelled or with digits
        ("al treilea", "al 3"),
        ("a patra", "a 4"),
        ("al 3-lea", "al 3"),
        ("a 3-a", "a 3"),
        ("a opta", "a 8"),
        ("al unsprezecelea", "al 11"),
        ("a unsprezecea", "a 11"),
        ("al douăzecilea", "al 20"),
        ("a douăzecea", "a 20"),
        ("al douăzeci și cincilea", "al 25"),
        # "întâi" before a month is its first day
        ("pe întâi decembrie", "pe 1 decembrie"),
        # The "de" of a discourse marker or a preposition after a number stays
        ("în 2024 de exemplu", "în 2024 de exemplu"),
        ("douăzeci de pe listă", "20 de pe listă"),
    ],
)
def test_spelled_numbers_become_digits(
    normalizer: RomanianNumberNormalizer, text: str, expected: str
) -> None:
    assert normalizer(text) == expected


@pytest.mark.parametrize(
    "text",
    [
        "un om",  # article, not a number
        "o zi",
        "am o casă",
        "mii de oameni",  # bare multiplier
        "și ea",
        "treilea",  # ordinal without "al"/"a"
    ],
)
def test_articles_and_bare_words_stay_words(
    normalizer: RomanianNumberNormalizer, text: str
) -> None:
    assert normalizer(text) == text


def test_empty_text(normalizer: RomanianNumberNormalizer) -> None:
    assert normalizer("") == ""


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("1200 €", "1200 euro"),
        ("1200€", "1200 euro"),
        ("€1200", "1200 euro"),
        ("50 $", "50 dolari"),
        ("o mie două sute de euro", "1200 euro"),
        # A symbol after an amount stays with it, not with the next number
        ("5 € 2 kilograme", "5 euro 2 kilograme"),
        ("5€ 2 kilograme", "5 euro 2 kilograme"),
        ("cinci € 2 kilograme", "5 euro 2 kilograme"),  # spelled numbers first
        ("€50 €100", "50 euro 100 euro"),  # each symbol keeps its own amount
        ("20 de €", "20 euro"),  # like "20 de euro"
    ],
)
def test_currency_symbols_read_as_romanian_speaks_them(
    text: str, expected: str
) -> None:
    from normalization.languages.romanian.operators import ROMANIAN_CONFIG

    normalizer = RomanianNumberNormalizer(ROMANIAN_CONFIG.currency_symbol_to_word)
    assert normalizer(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("trei kile jumate", "3 virgula 5 kile"),
        ("trei kilograme și jumătate", "3 virgula 5 kilograme"),
        ("trei și jumătate", "3 virgula 5"),
        ("opt ore și jumătate", "8 virgula 5 ore"),
        ("jumătate de pâine", "jumătate de pâine"),
        ("trei și jumătate de pâine", "3 și jumătate de pâine"),
        # With a noun, a "de" after the half is the noun's: 3,5 kg of apples
        ("trei kilograme și jumătate de mere", "3 virgula 5 kilograme de mere"),
        # "un"/"o" are 1 before a measure, whose decimal takes the plural (1,5 ore)
        ("o oră și jumătate", "1 virgula 5 ore"),
        ("un an și jumătate", "1 virgula 5 ani"),
        ("un kil jumate", "1 virgula 5 kil"),
        ("o casă și jumătate", "o casă și jumătate"),
        # Without "și", only after a measure
        ("cei doi vor jumătate", "cei 2 vor jumătate"),
        # After a multiplier, a decimal of it, as written
        ("două milioane și jumătate", "2 virgula 5 milioane"),
        ("trei mii și jumătate de lei", "3 virgula 5 mii de lei"),
    ],
)
def test_halves_after_an_amount_become_decimals(
    normalizer: RomanianNumberNormalizer, text: str, expected: str
) -> None:
    assert normalizer(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("doi și un sfert", "2 virgula 25"),
        ("doi și-un sfert", "2 virgula 25"),
        ("două ore și un sfert", "2 virgula 25 ore"),
        ("doi și un sfert la sută", "2 virgula 25 la sută"),
        ("un sfert de oră", "un sfert de oră"),
        ("trei și un sfert de pâine", "3 și un sfert de pâine"),
        ("o oră și un sfert", "1 virgula 25 ore"),
        ("un milion și un sfert", "1 virgula 25 milioane"),
    ],
)
def test_quarters_after_an_amount_become_decimals(
    normalizer: RomanianNumberNormalizer, text: str, expected: str
) -> None:
    assert normalizer(text) == expected
