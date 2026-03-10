from pathlib import Path
from typing import cast

import yaml

import normalization.languages  # noqa: F401 — triggers @register_language decorators
from normalization.languages.registery import get_language_registry
from normalization.pipeline.base import NormalizationPipeline
from normalization.steps import get_step_registry
from normalization.steps.base import TextStep, WordStep

_PRESETS_DIR = Path(__file__).parent.parent / "presets"


def _resolve_preset_path(preset: str | Path) -> Path:
    path = Path(preset)
    if path.exists() and path.is_file():
        return path
    if path.suffix in (".yaml", ".yml"):
        raise FileNotFoundError(f"Preset file not found: {path}")
    yaml_path = _PRESETS_DIR / f"{preset}.yaml"
    if not yaml_path.exists():
        available = [p.stem for p in _PRESETS_DIR.glob("*.yaml")]
        raise FileNotFoundError(
            f"No built-in preset named {preset!r}. Available presets: {available}"
        )
    return yaml_path


def load_pipeline(preset: str | Path, language: str) -> NormalizationPipeline:
    """
    Load a pipeline for a given language.

    ``preset`` can be:

    - A preset name (e.g. ``"gladia-3"``): loads the corresponding YAML from
      the package's built-in ``presets/`` directory.
    - A path to a YAML file (e.g. ``"path/to/my-preset.yaml"``): loads that
      file directly.

    Step ORDER within each stage is defined by the YAML list order,
    but the 3-stage structure (pre / word / post) is enforced.
    """
    config = yaml.safe_load(_resolve_preset_path(preset).read_text())

    language_registry = get_language_registry()
    operators = language_registry.get(language, language_registry["default"])()

    def resolve_steps(step_names: list[str], registry_key: str):
        registry = get_step_registry()[registry_key]
        return [registry[name]() for name in step_names]

    pipeline = NormalizationPipeline(
        name=config["name"],
        operators=operators,
        text_pre_steps=cast(
            list[TextStep],
            resolve_steps(config.get("stages", {}).get("text_pre", []), "text"),
        ),
        word_steps=cast(
            list[WordStep],
            resolve_steps(config.get("stages", {}).get("word", []), "word"),
        ),
        text_post_steps=cast(
            list[TextStep],
            resolve_steps(config.get("stages", {}).get("text_post", []), "text"),
        ),
    )
    pipeline.validate()
    return pipeline
