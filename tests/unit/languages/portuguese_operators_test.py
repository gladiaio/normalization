import pytest

from normalization.languages.portuguese.clitics import merge_hyphenated_clitics
from normalization.languages.portuguese.operators import PortugueseOperators
from normalization.pipeline.loader import load_pipeline


@pytest.fixture
def operators():
    return PortugueseOperators()


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("envie-me", "envieme"),
        ("Envie-me", "envieme"),
        ("diga-me", "digame"),
        ("mande-me o documento", "mandeme o documento"),
        ("fale-me", "faleme"),
    ],
)
def test_merge_hyphenated_clitics(text: str, expected: str):
    assert merge_hyphenated_clitics(text) == expected


def test_portuguese_clitic_pipeline_variants():
    pipeline = load_pipeline("gladia-3", "pt")
    for variant in ("envie-me", "enviame", "envie me"):
        assert pipeline.normalize(variant) == pipeline.normalize("enviame")

    for variant in ("diga-me", "digame", "diga me"):
        assert pipeline.normalize(variant) == pipeline.normalize("digame")


def test_portuguese_filler_removal():
    pipeline = load_pipeline("gladia-3", "pt")
    assert pipeline.normalize("eh entao sim") == pipeline.normalize("sim")
    assert pipeline.normalize("ah mm sim") == pipeline.normalize("sim")
    # Meaningful affirmatives / idioms must survive normalization
    assert pipeline.normalize("claro estou") == pipeline.normalize("claro estou")
    assert pipeline.normalize("esta tudo bem") == pipeline.normalize("esta tudo bem")
    assert pipeline.normalize("e pronto foi assim") == pipeline.normalize(
        "e pronto foi assim"
    )


def test_portuguese_pra_para():
    pipeline = load_pipeline("gladia-3", "pt")
    assert pipeline.normalize("pra trabalhar") == pipeline.normalize("para trabalhar")


def test_portuguese_gender_and_spelling_variants():
    pipeline = load_pipeline("gladia-3", "pt")
    assert pipeline.normalize("propria") == pipeline.normalize("proprio")
    assert pipeline.normalize("maioritariamente") == pipeline.normalize("maioritario")
    assert pipeline.normalize("media") == pipeline.normalize("medio")


def test_portuguese_email_and_number_variants():
    pipeline = load_pipeline("gladia-3", "pt")
    assert pipeline.normalize("emails") == pipeline.normalize("email")
    assert pipeline.normalize("e-mails") == pipeline.normalize("email")
    assert pipeline.normalize("turnos rotativos") == pipeline.normalize(
        "turno rotativo"
    )
    assert pipeline.normalize("em quantos pesos") == pipeline.normalize(
        "de quanto peso"
    )


def test_portuguese_pt_pt_br_variants():
    pipeline = load_pipeline("gladia-3", "pt")
    assert pipeline.normalize("controles") == pipeline.normalize("controlos")
    assert pipeline.normalize("equipe") == pipeline.normalize("equipa")


def test_portuguese_brand_variants():
    pipeline = load_pipeline("gladia-3", "pt")
    assert pipeline.normalize("adeco") == pipeline.normalize("adecco")
    assert pipeline.normalize("adec") == pipeline.normalize("adecco")


def test_portuguese_written_numbers():
    pipeline = load_pipeline("gladia-3", "pt")
    assert pipeline.normalize("vinte e tres") == "23"
    assert pipeline.normalize("cem euros") == "100 euros"
