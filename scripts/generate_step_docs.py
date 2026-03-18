#!/usr/bin/env python3
"""
Generate Markdown documentation for all registered normalization steps.

Usage:
    python scripts/generate_step_docs.py [output_path]

Output defaults to docs/steps.md.
"""

import inspect
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# Import all steps to trigger @register_step decorators
import normalization.steps  # noqa: E402, F401
from normalization.steps.base.protect_step import ProtectStep  # noqa: E402
from normalization.steps.base.restore_step import RestoreStep  # noqa: E402
from normalization.steps.base.text_step import TextStep  # noqa: E402
from normalization.steps.base.word_step import WordStep  # noqa: E402
from normalization.steps.registry import get_step_registry  # noqa: E402

_BASE_CLASS_PRIORITY = (ProtectStep, RestoreStep, TextStep, WordStep)


def _base_class_name(cls: type) -> str:
    for base in cls.__mro__[1:]:
        if base in _BASE_CLASS_PRIORITY:
            return base.__name__
    return "TextStep"


def _format_step(cls: type, name: str) -> str:
    base = _base_class_name(cls)
    doc = inspect.getdoc(cls) or "_No description._"

    lines = [f"### `{name}`", ""]
    lines.append(f"**Base class:** `{base}`")
    lines.append("")
    lines.append(doc)
    lines.append("")
    return "\n".join(lines)


def generate(output_path: Path) -> None:
    registry = get_step_registry()
    text_reg = registry["text"]
    word_reg = registry["word"]

    out_lines = [
        "# Step Reference",
        "",
        "Auto-generated — do not edit by hand. Run `scripts/generate_step_docs.py` to update.",
        "",
        "## Text Steps",
        "",
    ]

    for name in sorted(text_reg):
        out_lines.append(_format_step(text_reg[name], name))

    out_lines += ["## Word Steps", ""]

    for name in sorted(word_reg):
        out_lines.append(_format_step(word_reg[name], name))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(out_lines))

    print(f"Written {len(text_reg) + len(word_reg)} steps to {output_path}")


if __name__ == "__main__":
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "docs" / "steps.md"
    generate(out)
