from pathlib import Path
from typing import cast

import yaml

import normalization.languages  # noqa: F401 — triggers @register_language decorators
from normalization.languages.registery import get_language_registry
from normalization.pipeline.base import NormalizationPipeline
from normalization.steps import get_step_registry
from normalization.steps.base import TextStep, WordStep


def load_pipeline(yaml_path: str | Path, language: str) -> NormalizationPipeline:
    """
    Load a pipeline from a YAML preset file for a given language.

    The YAML defines which steps are active per stage.
    Step ORDER within each stage is defined by the YAML list order,
    but the 3-stage structure (pre / word / post) is enforced.
    """
    config = yaml.safe_load(Path(yaml_path).read_text())

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
