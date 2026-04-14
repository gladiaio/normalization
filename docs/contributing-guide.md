# Contributing guide

Detailed reference for contributors. Read this before adding a step or language.

## Architecture at a glance

Every pipeline runs exactly **three stages**, always in this order:

1. **Text pre-processing** — full-text transforms before word splitting (placeholder protection, symbol conversion, contraction expansion, …)
2. **Word processing** — per-token transforms after splitting on spaces (replacements, filler removal, …)
3. **Text post-processing** — full-text cleanup after rejoining words (placeholder restoration, digit collapsing, …)

This ordering is a hard constraint — some steps depend on earlier steps having run. See the [README](../README.md) for more detail.

---

## Adding a new language — checklist

- [ ] Create `languages/{lang}/` with `operators.py`, `replacements.py`, `__init__.py`
- [ ] Put all word-level substitutions in `replacements.py`; do not add inline entries in `operators.py`
- [ ] Instantiate a `LanguageConfig` in `operators.py`, filling in all required fields and any optional dict fields your language needs (`time_words`, `sentence_replacements`, etc.)
- [ ] Subclass `LanguageOperators`, overriding only methods where the _algorithm_ differs (not just the data)
- [ ] If the language has digit words, populate `digit_words` in `LanguageConfig`
- [ ] If the language uses spoken time patterns, populate `time_words` with all needed word→digit mappings; if it also uses compound minute expressions (e.g. "twenty-one"), override `get_compound_minutes()` — do **not** put this in config
- [ ] If number expansion is needed and the algorithm is complex, implement it in a `number_normalizer.py` file and override `expand_written_numbers`; otherwise do not create the file
- [ ] Decorate the class with `@register_language`
- [ ] Add one import to `languages/__init__.py`
- [ ] Add tests in `tests/unit/languages/`
- [ ] Add a CSV file `tests/e2e/files/{preset}/{language_code}.csv` for each relevant preset (e.g. `tests/e2e/files/gladia-3/fr.csv`)

### Language data vs. language behavior

This is the central design rule. Ask: "does the _logic_ change by language, or just the _values_?"

**`LanguageConfig` (data)** — everything that can be expressed as a value: strings, lists, dicts. Separator characters, currency words, filler words, digit words, number words, time words, sentence replacements. Optional fields default to `None`; steps that read them skip gracefully when `None`.

**`LanguageOperators` (behavior)** — only methods where the _algorithm itself_ varies by language. Examples: `expand_contractions`, `expand_written_numbers`, `normalize_numeric_time_formats`, `get_compound_minutes`. If the algorithm is generic and only the _data_ differs, put the data in `LanguageConfig` and the algorithm in the step — not in the operator.

---

## Adding a new step — checklist

- [ ] Add the class to the appropriate file in `steps/text/` or `steps/word/`
- [ ] Set a unique `name` class attribute
- [ ] Decorate with `@register_step`
- [ ] Add one import to `steps/text/__init__.py` or `steps/word/__init__.py`
- [ ] Place the algorithm in `__call__`; read language data from `operators.config.*`; call operator methods only for genuinely behavioral differences
- [ ] If the step reads an optional `LanguageConfig` field, guard with `if operators.config.field is None: return text`
- [ ] Add unit tests in `tests/unit/steps/`
- [ ] If it involves placeholder protection, add both protect and restore to `steps/text/placeholders.py` and update `pipeline/base.py`'s `validate()` accordingly
- [ ] Add the step name to relevant preset YAMLs if needed (new preset version if existing presets are affected)
- [ ] If you added or changed the class docstring, run `uv run scripts/generate_step_docs.py` to regenerate `docs/steps.md`

### Choosing a base class

Pick the narrowest one that fits your step.

**`WordStep`** — use when your transformation operates on a single token in isolation, with no knowledge of neighboring words. This is the only base class for Stage 2 steps.

```python
@register_step
class MyWordStep(WordStep):
    name = "my_word_step"

    def __call__(self, word: str, operators: LanguageOperators) -> str:
        ...
```

**`TextStep`** — the general-purpose base for Stage 1 and Stage 3. Use it when your transformation needs to see the full string, or when none of the more specific bases below fit.

```python
@register_step
class MyTextStep(TextStep):
    name = "my_text_step"

    def __call__(self, text: str, operators: LanguageOperators) -> str:
        ...
```

**`ProtectStep`** — a specialization of `TextStep` for replacing a character with a placeholder token. Implement `_pattern`, which returns a compiled regex with **exactly two capture groups** (what comes before and after the character being replaced). The `__call__` is fixed: it applies the pattern as `\1{placeholder}\2`.

```python
@register_step
class MyProtectStep(ProtectStep):
    name = "my_protect_step"
    placeholder = ProtectPlaceholder.MY_PLACEHOLDER

    def _pattern(self, operators: LanguageOperators) -> re.Pattern:
        return re.compile(r"(\d+)X(\d+)")  # two capture groups required
```

Use `ProtectStep` when: one regex pattern maps to exactly one placeholder substitution.

Use `TextStep` directly instead when: a single pass must protect two different symbols, the replacement needs to absorb surrounding whitespace with `\s*`, or the replacement is a per-match function rather than a fixed template.

**`RestoreStep`** — a specialization of `TextStep` for restoring a placeholder back to a string. Implement `_replacement`, which returns the string to substitute in. The `__call__` does a plain `str.replace` of the placeholder (and its case-folded form).

```python
@register_step
class MyRestoreStep(RestoreStep):
    name = "my_restore_step"
    placeholder = ProtectPlaceholder.MY_PLACEHOLDER

    def _replacement(self, operators: LanguageOperators) -> str:
        return operators.config.some_word or " "
```

Use `RestoreStep` when: restoration is a straight token swap with no surrounding whitespace to absorb and no additional logic needed.

Use `TextStep` directly instead when: the placeholder was inserted with spaces around it (requiring `re.sub` with `\s*` to avoid double spaces), the marker should be deleted entirely rather than replaced, or post-replacement cleanup is needed.

---

## Writing tests

### Unit tests for a step

Unit tests live under `tests/unit/steps/text/` or `tests/unit/steps/word/`, mirroring the step file structure.

The `tests/unit/steps/text/conftest.py` provides two fixtures and a helper:

- `operators` — a bare `LanguageOperators()` instance (language-agnostic)
- `english_operators` — an `EnglishOperators()` instance
- `assert_text_step_registered(step_cls)` — verifies the step is in the registry under its name

Every test file for a step should at minimum:

1. Assert the step is registered.
2. Instantiate the step with `MyStep()` and call it directly: `MyStep()(text, operators)`.
3. Mutate `operators.config` fields in-place to cover different language configurations without creating a full language.

```python
# tests/unit/steps/text/my_step_test.py
from normalization.languages.base import LanguageOperators
from normalization.steps.text.my_module import MyStep

from .conftest import assert_text_step_registered


def test_step_is_registered():
    assert_text_step_registered(MyStep)


def test_my_step_basic(operators: LanguageOperators):
    result = MyStep()("some input", operators)
    assert result == "expected output"


def test_my_step_with_config(operators: LanguageOperators):
    operators.config.some_field = "custom_value"
    result = MyStep()("some input", operators)
    assert result == "expected output with custom value"


def test_my_step_with_english(english_operators):
    result = MyStep()("some input", english_operators)
    assert result == "english-specific output"
```

### E2E tests for a preset

E2E tests validate the full pipeline (preset + language) against CSV fixtures. The test runner lives in `tests/e2e/normalization_test.py` and CSV files are organized under `tests/e2e/files/`.

**Directory structure** — one folder per preset, one CSV per language:

```
tests/e2e/files/
  gladia-3/
    default.csv
    de.csv
    en.csv
    fr.csv
    it.csv
```

**CSV format** — two columns (`input,expected`), no quoting needed unless the value contains a comma:

```
input,expected
"$1,000,000",1000000 dollars
hello world,hello world
```

The language is derived from the filename (e.g. `fr.csv` → language code `fr`). Use `default.csv` for the language-agnostic fallback.

**Adding test cases for an existing preset** — drop rows into the appropriate `{language_code}.csv` file, or create a new CSV if the language isn't covered yet. Tests are discovered automatically.

**Registering a new preset** — add a block to `normalization_test.py` following the existing pattern:

```python
_MY_PRESET_DIR = _FILES_DIR / "my-preset"
_MY_PRESET_BY_LANGUAGE = _discover_preset_tests(_MY_PRESET_DIR)
_MY_PRESET_PIPELINES: dict[str, NormalizationPipeline] = {}

for _language in sorted(_MY_PRESET_BY_LANGUAGE):
    globals()[f"test_my_preset_{_language}"] = _make_test(
        "my-preset", _language, _MY_PRESET_BY_LANGUAGE[_language], _MY_PRESET_PIPELINES
    )
```

Pipelines are cached per language to avoid reloading for each parametrized case.

---

## Key design rules

- **Data vs. behavior**: if only the _values_ change by language, put them in `LanguageConfig`. If the _algorithm_ changes, override a method in `LanguageOperators`.
- **Steps are language-agnostic**: a step must not contain any language-specific logic or string literals. Read from `operators.config.*` or call `operators.method()`.
- **Presets are immutable**: never modify a published preset YAML — new behavior means a new preset file.
- **Placeholder pairs**: every `protect_*` step in Stage 1 must have a matching `restore_*` in Stage 3. The pipeline validates this at load time.
- **Language folders are self-contained**: everything specific to a language lives inside its folder. Helpers used only by one language (e.g. `number_normalizer.py`) go in that language's folder, not in `steps/`.