## What does this PR do?

<!-- One sentence: what changed and why. -->

## Type of change

- [ ] New language
- [ ] Edit existing language (fix a replacement, tweak config, …)
- [ ] New normalization step
- [ ] Edit existing step (bug fix, behaviour change)
- [ ] New preset version
- [ ] Bug fix (other)
- [ ] Refactor / docs / CI

---

## Checklist

**Only fill in the section(s) that match your change — delete the rest.**

---

### New language

- [ ] Created `normalization/languages/{lang}/` with `operators.py`, `replacements.py`, `__init__.py`
- [ ] Word substitutions are in `replacements.py` (not hardcoded in `operators.py`)
- [ ] `LanguageConfig` is filled in with the language's data (separators, currency words, digit words, …)
- [ ] Subclassed `LanguageOperators` — only override methods where the **logic** changes, not just the data
- [ ] Class is decorated with `@register_language` and imported in `normalization/languages/__init__.py`
- [ ] Unit tests added in `tests/unit/languages/`
- [ ] E2e CSV added in `tests/e2e/files/{preset}/{lang}.csv` (e.g. `tests/e2e/files/gladia-3/fr.csv`)

---

### Edit existing language

- [ ] New/changed word substitutions go in `replacements.py`, not inline in `operators.py`
- [ ] If you changed a config field that can be `None`: the step reading it still handles `None` gracefully
- [ ] Unit tests updated or added
- [ ] E2e CSV updated if the expected output changed

---

### New step

- [ ] Unique `name` class attribute set (this is the key used in YAML presets)
- [ ] Decorated with `@register_step` and imported in `steps/text/__init__.py` or `steps/word/__init__.py`
- [ ] No hardcoded language values — read data from `operators.config.*` instead
- [ ] If placeholder-based: protect + restore are both in `steps/text/placeholders.py` and `pipeline/base.py`'s `validate()` is updated
- [ ] Unit tests added in `tests/unit/steps/`
- [ ] Step name added to the relevant preset YAML — or a **new preset file** created if existing presets are affected
- [ ] If the docstring changed: ran `uv run scripts/generate_step_docs.py`

---

### Edit existing step

- [ ] Step `name` is unchanged — if the output changes, create a new step name + new preset instead
- [ ] No language-specific logic or string literals added inside the step
- [ ] Unit tests updated or added
- [ ] If the docstring changed: ran `uv run scripts/generate_step_docs.py`

---

### Preset change

- [ ] Existing preset files are **not modified** — new behaviour goes in a new preset file
- [ ] `pipeline.validate()` passes (runs automatically via `loader.py`)

---

## How was this tested?

```
uv run pytest tests/
```
