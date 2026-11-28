"""gladia-3 keeps its published output on digit and spelled ordinals; gladia-4 brings
them to the same form. The gladia-3 values are what the preset gave before gladia-4."""

import pytest

from normalization.pipeline.loader import load_pipeline


@pytest.mark.parametrize(
    ("language", "text", "gladia_3", "gladia_4"),
    [
        ("fr", "le 1er mai", "le 1 e r mai", "le 1 mai"),
        ("da", "den første 2 maj", "den 12 maj", "den 1 2 maj"),
        ("nl", "de 1ste mei", "de 1 is het e mei", "de 1 mei"),
    ],
)
def test_ordinals_by_preset(
    language: str, text: str, gladia_3: str, gladia_4: str
) -> None:
    assert load_pipeline("gladia-3", language).normalize(text) == gladia_3
    assert load_pipeline("gladia-4", language).normalize(text) == gladia_4
