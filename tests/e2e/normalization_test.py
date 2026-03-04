import csv
from dataclasses import dataclass
from pathlib import Path

import pytest

from normalization.pipeline.base import NormalizationPipeline
from normalization.pipeline.loader import load_pipeline

_FILES_DIR = Path(__file__).resolve().parent / "files"
_PRESETS_DIR = Path(__file__).resolve().parents[2] / "normalization" / "presets"


@dataclass
class NormalizationTest:
    language: str
    input: str
    expected: str


def _load_tests_from_csv(csv_path: Path) -> list[NormalizationTest]:
    rows: list[NormalizationTest] = []
    with csv_path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rows.append(
                NormalizationTest(
                    language=row["language"],
                    input=row["input"],
                    expected=row["expected"],
                )
            )
    return rows


def _case_ids(cases: list[NormalizationTest]) -> list[str]:
    return [f"{test.language}:{test.input[:60]}" for test in cases]


def _load_pipeline(preset_path: Path, language: str) -> NormalizationPipeline:
    if language not in _GLADIA_3_PIPELINES:
        _GLADIA_3_PIPELINES[language] = load_pipeline(
            preset_path,
            language,
        )
    return _GLADIA_3_PIPELINES[language]


# ---------------------------------------------------------------------------
# gladia_3
# ---------------------------------------------------------------------------

_GLADIA_3_CSV = _FILES_DIR / "gladia-3.csv"
_GLADIA_3_TESTS = _load_tests_from_csv(_GLADIA_3_CSV) if _GLADIA_3_CSV.exists() else []
_GLADIA_3_PIPELINES: dict[str, NormalizationPipeline] = {}


@pytest.mark.parametrize(
    "test",
    _GLADIA_3_TESTS,
    ids=_case_ids(_GLADIA_3_TESTS),
)
def test_gladia_3(test: NormalizationTest) -> None:
    pipeline = _load_pipeline(_PRESETS_DIR / "gladia-3.yaml", test.language)
    result = pipeline.normalize(test.input)
    assert result == test.expected, (
        f"\n  input:    {test.input!r}"
        f"\n  expected: {test.expected!r}"
        f"\n  got:      {result!r}"
    )
