import pytest

from normalization.languages.romanian.time_normalizer import RomanianTimeNormalizer


@pytest.fixture
def normalizer() -> RomanianTimeNormalizer:
    return RomanianTimeNormalizer()


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        # Half past: formal and informal
        ("la ora opt și jumătate", "la ora 8:30"),
        ("la opt jumate", "la 8:30"),
        ("e opt și jumate", "e 8:30"),
        # Quarter past, including the elided "și-un"
        ("la opt și un sfert", "la 8:15"),
        ("la opt și-un sfert", "la 8:15"),
        # Quarter to and minutes to: the hour before
        ("la opt fără un sfert", "la 7:45"),
        ("la opt fără zece", "la 7:50"),
        ("la unu fără un sfert", "la 12:45"),
        # Minutes after "la"/"ora"
        ("la ora opt și zece", "la ora 8:10"),
        ("la șapte patruzeci și cinci", "la 7:45"),
        ("la ora douăzeci și unu treizeci", "la ora 21:30"),
        # Digits for the hour, and times written with a dot
        ("la 8 jumate", "la 8:30"),
        ("la ora 8.30", "la ora 8:30"),
        # Punctuation after the time is kept
        ("Ne vedem la opt și jumătate.", "Ne vedem la 8:30."),
        # "este" (the full "e") and "după" are cues too
        ("este opt și jumătate", "este 8:30"),
        ("după opt fără un sfert", "după 7:45"),
        # After "ora" any minutes follow "și", not only round ones
        ("la ora opt și cincisprezece", "la ora 8:15"),
        # A range of times is not a change of value; an arrival is a time
        ("ne vedem de la opt la nouă și jumătate", "ne vedem de la opt la 9:30"),
        ("a ajuns la opt și jumătate", "a ajuns la 8:30"),
    ],
)
def test_spoken_times_become_clock_times(
    normalizer: RomanianTimeNormalizer, text: str, expected: str
) -> None:
    assert normalizer(text) == expected


@pytest.mark.parametrize(
    "text",
    [
        "mai am trei și jumătate",  # a quantity, no time cue
        "e opt și zece",  # minute numbers only after "la"/"ora"
        "la ora opt",  # an hour alone stays for the number normalizer
        "la ion acasă",
        "am plătit la trei oameni",
        "costă 8.30 lei",  # a dotted number without a time cue
        # An amount word after the phrase makes it a quantity, whatever the cue
        "a crescut la trei și jumătate la sută",
        "e doi și un sfert la sută",
        "a urcat la doi și jumătate milioane",
        "au crescut la trei și jumătate mii de lei",
        "e trei și jumătate lei",
        "e trei și jumătate %",
        "a ajuns la zece douăzeci de lei",  # "de" before the unit
        "de la trei și jumătate la cinci la sută",  # a range of amounts
        "a ajuns la 8.30 lei",  # a dotted amount
        "până la 15.03.2024",  # a dotted date
        "la opt și cincisprezece oameni",  # after "la", only round minutes follow "și"
        # After a verb of change, the new value, its unit often left out
        "inflația a crescut la trei și jumătate",
        "rata a scăzut de la patru la trei și jumătate",
        "prețul a urcat până la doi și un sfert",
    ],
)
def test_other_phrases_are_left_alone(
    normalizer: RomanianTimeNormalizer, text: str
) -> None:
    assert normalizer(text) == text
