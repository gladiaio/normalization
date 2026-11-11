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
        ("bem-te-vi", "bem-te-vi"),
    ],
)
def test_merge_hyphenated_clitics(text: str, expected: str):
    assert merge_hyphenated_clitics(text) == expected


def test_portuguese_clitic_pipeline_variants():
    pipeline = load_pipeline("gladia-3", "pt")
    assert pipeline.normalize("envie-me") == "enviame"
    assert pipeline.normalize("enviame") == "enviame"
    assert pipeline.normalize("envie me") == "enviame"
    assert pipeline.normalize("diga-me") == "digame"
    assert pipeline.normalize("digame") == "digame"
    assert pipeline.normalize("diga me") == "digame"
    assert pipeline.normalize("fale me") == "faleme"


def test_portuguese_filler_removal():
    pipeline = load_pipeline("gladia-3", "pt")
    assert pipeline.normalize("eh entao sim") == "entao sim"
    assert pipeline.normalize("ah mm sim") == "sim"
    assert pipeline.normalize("portanto nao") == "portanto nao"
    assert pipeline.normalize("claro estou") == "claro estou"
    assert pipeline.normalize("esta tudo bem") == "esta tudo bem"
    assert pipeline.normalize("e pronto foi assim") == "e pronto foi assim"


def test_portuguese_pra_para():
    pipeline = load_pipeline("gladia-3", "pt")
    assert pipeline.normalize("pra trabalhar") == "para trabalhar"


def test_portuguese_email_variants():
    pipeline = load_pipeline("gladia-3", "pt")
    assert pipeline.normalize("emails") == "email"
    assert pipeline.normalize("e-mails") == "email"


def test_portuguese_pt_pt_br_variants():
    pipeline = load_pipeline("gladia-3", "pt")
    assert pipeline.normalize("controles") == "controlos"
    assert pipeline.normalize("equipe") == "equipa"


def test_portuguese_written_numbers_and_mixed_forms():
    pipeline = load_pipeline("gladia-3", "pt")
    assert pipeline.normalize("vinte e tres") == "23"
    assert pipeline.normalize("cem euros") == "100 euros"
    assert pipeline.normalize("25 mil euros") == "25000 euros"
    assert pipeline.normalize("uma pessoa") == "uma pessoa"
    assert pipeline.normalize("duas pessoas") == "duas pessoas"
    assert pipeline.normalize("R$ 50") == "50 reais"


def test_portuguese_numeric_um_context(operators):
    assert operators.fix_one_word_in_numeric_contexts("10 um") == "10 1"
    assert operators.fix_one_word_in_numeric_contexts("um carro") == "um carro"
