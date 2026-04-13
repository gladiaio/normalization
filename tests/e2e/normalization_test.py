import csv
from dataclasses import dataclass
from pathlib import Path

import pytest

from normalization.pipeline.base import NormalizationPipeline
from normalization.pipeline.loader import load_pipeline

_FILES_DIR = Path(__file__).resolve().parent / "files"


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
    return [test.input[:60] for test in cases]


def _group_by_language(
    tests: list[NormalizationTest],
) -> dict[str, list[NormalizationTest]]:
    groups: dict[str, list[NormalizationTest]] = {}
    for t in tests:
        groups.setdefault(t.language, []).append(t)
    return groups


def _load_pipeline(preset_name_or_path: str, language: str) -> NormalizationPipeline:
    if language not in _GLADIA_3_PIPELINES:
        _GLADIA_3_PIPELINES[language] = load_pipeline(
            preset_name_or_path,
            language,
        )
    return _GLADIA_3_PIPELINES[language]


# ---------------------------------------------------------------------------
# gladia_3
# ---------------------------------------------------------------------------

_GLADIA_3_CSV = _FILES_DIR / "gladia-3.csv"
_GLADIA_3_TESTS = _load_tests_from_csv(_GLADIA_3_CSV) if _GLADIA_3_CSV.exists() else []
_GLADIA_3_PIPELINES: dict[str, NormalizationPipeline] = {}


def _make_gladia_3_test(language: str, cases: list[NormalizationTest]):
    @pytest.mark.parametrize("test", cases, ids=_case_ids(cases))
    def _test(test: NormalizationTest) -> None:
        pipeline = _load_pipeline("gladia-3", language)
        result = pipeline.normalize(test.input)
        assert result == test.expected, (
            f"\n  input:    {test.input!r}"
            f"\n  expected: {test.expected!r}"
            f"\n  got:      {result!r}"
        )

    _test.__name__ = f"test_gladia_3_{language}"
    return _test


_GLADIA_3_BY_LANGUAGE = _group_by_language(_GLADIA_3_TESTS)

for _language in sorted(_GLADIA_3_BY_LANGUAGE):
    globals()[f"test_gladia_3_{_language}"] = _make_gladia_3_test(
        _language, _GLADIA_3_BY_LANGUAGE[_language]
    )
