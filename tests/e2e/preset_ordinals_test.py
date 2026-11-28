"""gladia-3 keeps its published output on digit and spelled ordinals; gladia-4 writes
both forms as digits plus one suffix per language. The gladia-3 values are what the
preset gave before gladia-4."""

import pytest

from normalization.pipeline.loader import load_pipeline


@pytest.mark.parametrize(
    ("language", "text", "gladia_3", "gladia_4"),
    [
        ("fr", "le 1er mai", "le 1 e r mai", "le 1er mai"),
        ("fr", "le premier mai", "le premier mai", "le 1er mai"),
        ("da", "den første 2 maj", "den 12 maj", "den 1. 2 maj"),
        ("nl", "de 1ste mei", "de 1 is het e mei", "de 1e mei"),
        ("en", "the first 2 May", "the 12 may", "the 1st 2 may"),
        ("de", "am 1. 2 Mai", "am 12 mai", "am 1. 2 mai"),
    ],
)
def test_ordinals_by_preset(
    language: str, text: str, gladia_3: str, gladia_4: str
) -> None:
    assert load_pipeline("gladia-3", language).normalize(text) == gladia_3
    assert load_pipeline("gladia-4", language).normalize(text) == gladia_4


@pytest.mark.parametrize(
    ("language", "text"),
    [
        ("fr", "le un mai"),
        ("fr", "le deux mai"),
        ("fr", "le 2 mai"),
        ("fr", "chapitre un"),
        ("fr", "page 3"),
        ("en", "May one"),
        ("en", "page one"),
        ("de", "am 1 Mai"),
        ("da", "den 1 maj"),
        ("es", "el uno de mayo"),
        ("es", "el 2 de mayo"),
        ("it", "il 2 maggio"),
        ("nl", "1 mei"),
        ("sv", "den 1 maj"),
        ("no", "den 1 mai"),
        ("pt", "o 2 de maio"),
    ],
)
def test_cardinal_stays_a_cardinal(language: str, text: str) -> None:
    """A cardinal is never turned into an ordinal: gladia-4 gives gladia-3's output."""
    assert load_pipeline("gladia-4", language).normalize(text) == (
        load_pipeline("gladia-3", language).normalize(text)
    )
