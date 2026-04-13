## What does this PR do?

<!-- One-sentence summarizing of the change. -->

## Type of change

- [ ] New language (`languages/{lang}/`)
- [ ] New step (`steps/text/` or `steps/word/`)
- [ ] New preset version (`presets/`)
- [ ] Bug fix
- [ ] Refactor / internal cleanup
- [ ] Docs / CI

## Checklist

### New language

- [ ] Created `languages/{lang}/` with `operators.py`, `replacements.py`, `__init__.py`
- [ ] All word-level substitutions are in `replacements.py`, not inline in `operators.py`
- [ ] Decorated operators class with `@register_language`
- [ ] Added one import line to `languages/__init__.py`
- [ ] Added unit tests in `tests/unit/languages/`
- [ ] Added a per-language CSV in `tests/e2e/files/{preset}/` (e.g. `tests/e2e/files/gladia-3/fr.csv`)

### New step

- [ ] `name` class attribute is unique and matches the YAML key
- [ ] Decorated with `@register_step`
- [ ] Added one import line to `steps/text/__init__.py` or `steps/word/__init__.py`
- [ ] Algorithm reads data from `operators.config.*`, no hardcoded language-specific values
- [ ] Optional config fields are guarded with `if operators.config.field is None: return text`
- [ ] Placeholder protect/restore pairs are both in `steps/text/placeholders.py` and `pipeline/base.py`'s `validate()` is updated
- [ ] Added unit tests in `tests/unit/steps/`
- [ ] Added step name to relevant preset YAMLs (new preset file if existing presets are affected)
- [ ] If the class docstring was added or changed, ran `uv run scripts/generate_step_docs.py` to regenerate `docs/steps.md`

### Preset change

- [ ] Existing preset files are not modified — new behavior uses a new preset version file

## Tests

<!-- Describe what was tested and how. -->
