import csv
from dataclasses import dataclass
from pathlib import Path

import pytest

from normalization.pipeline.base import NormalizationPipeline
from normalization.pipeline.loader import load_pipeline

_FILES_DIR = Path(__file__).resolve().parent / "files"


@dataclass
class NormalizationTest:
    input: str
    expected: str


def _load_tests_from_csv(csv_path: Path) -> list[NormalizationTest]:
    rows: list[NormalizationTest] = []
    with csv_path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rows.append(
                NormalizationTest(
                    input=row["input"],
                    expected=row["expected"],
                )
            )
    return rows


def _case_ids(cases: list[NormalizationTest]) -> list[str]:
    return [test.input[:60] for test in cases]


def _discover_preset_tests(
    preset_dir: Path,
) -> dict[str, list[NormalizationTest]]:
    """Scan a preset directory for per-language CSV files.

    Returns a dict mapping language code (filename stem) to test cases.
    """
    tests: dict[str, list[NormalizationTest]] = {}
    if not preset_dir.is_dir():
        return tests
    for csv_path in sorted(preset_dir.glob("*.csv")):
        language = csv_path.stem
        cases = _load_tests_from_csv(csv_path)
        if cases:
            tests[language] = cases
    return tests


# ---------------------------------------------------------------------------
# One test per preset folder under files/ and per language CSV in it:
# test_gladia_3_fr runs files/gladia-3/fr.csv through the gladia-3 preset.
# ---------------------------------------------------------------------------

_PIPELINES: dict[tuple[str, str], NormalizationPipeline] = {}


def _load_pipeline(preset: str, language: str) -> NormalizationPipeline:
    key = (preset, language)
    if key not in _PIPELINES:
        _PIPELINES[key] = load_pipeline(preset, language)
    return _PIPELINES[key]


def _make_test(preset: str, language: str, cases: list[NormalizationTest]):
    @pytest.mark.parametrize("test", cases, ids=_case_ids(cases))
    def _test(test: NormalizationTest) -> None:
        pipeline = _load_pipeline(preset, language)
        result = pipeline.normalize(test.input)
        assert result == test.expected, (
            f"\n  input:    {test.input!r}"
            f"\n  expected: {test.expected!r}"
            f"\n  got:      {result!r}"
        )

    _test.__name__ = f"test_{preset.replace('-', '_')}_{language}"
    return _test


for _preset_dir in sorted(p for p in _FILES_DIR.iterdir() if p.is_dir()):
    _by_language = _discover_preset_tests(_preset_dir)
    for _language in sorted(_by_language):
        _t = _make_test(_preset_dir.name, _language, _by_language[_language])
        globals()[_t.__name__] = _t
