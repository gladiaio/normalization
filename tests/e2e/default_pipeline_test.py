from pathlib import Path

from normalization.pipeline.loader import load_pipeline

_PRESETS_DIR = Path(__file__).resolve().parents[2] / "normalization" / "presets"


def test_default_pipeline():
    """
    Test that the default pipeline normalizes the text correctly.
    """
    pipeline = load_pipeline(_PRESETS_DIR / "gladia-3.yaml", "default")
    assert pipeline.normalize("Hello, world!") == "hello world"


def test_unknown_language():
    """
    Test that the default pipeline raises an error for an unknown language.
    """
    pipeline = load_pipeline(_PRESETS_DIR / "gladia-3.yaml", "unknown")
    assert pipeline.normalize("ça va?!") == "ca va"
