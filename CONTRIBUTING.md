# Contributing

Thanks for your interest in `gladia-normalization`! Here's how to get involved.

## Reporting bugs

Open an issue with steps to reproduce, expected vs actual behavior, and your environment (Python version, OS, package version).

## Submitting changes

1. **Fork the repo and create a branch**: `git checkout -b feat/my-feature`
2. **Make your changes and add tests**
3. **Run the checks**:
   ```bash
   uv run pytest               # run tests
   uv run ruff check .         # lint
   uv run ruff format .        # format
   uv run ty check             # type-check
   ```
4. **Push your branch**: `git push origin your-feature-branch`
5. **Create a PR**: Go to GitHub and create a pull request
6. **Fill out the PR template**: Provide clear description of changes
7. **Wait for review**: Maintainers will review and provide feedback
8. **Address feedback**: Make requested changes and push updates
9. **Merge**: Once approved, your PR will be merged!

### Pre-commit hooks

The project uses [pre-commit](https://pre-commit.com/) to enforce linting, formatting, and commit message conventions automatically. Install the hooks once after cloning:

```bash
uv run pre-commit install --install-hooks
```

This will run Ruff (lint + format) and ty (type-check) on every commit, and validate your commit message on `commit-msg`.

## Commit style

We use [Conventional Commits](https://www.conventionalcommits.org/): pre-fix your commit with `feat:`, `fix:`, `docs:`, `chore:`, etc.

## Architecture at a glance

Every pipeline runs exactly **three stages**, always in this order:

1. **Text pre-processing** — full-text transforms before word splitting (placeholder protection, symbol conversion, contraction expansion, …)
2. **Word processing** — per-token transforms after splitting on spaces (replacements, filler removal, …)
3. **Text post-processing** — full-text cleanup after rejoining words (placeholder restoration, digit collapsing, …)

This ordering is a hard constraint — some steps depend on earlier steps having run. See the [README](./README.md) for more detail.

## Adding a new step

1. Create or extend a file under `normalization/steps/text/` or `normalization/steps/word/`.
2. Decorate the class with `@register_step` and set a unique `name` attribute.
3. Add an import to `steps/text/__init__.py` or `steps/word/__init__.py`.
4. Add unit tests under `tests/unit/steps/`.
5. Add the step name to the relevant preset YAML, or create a new preset version.
6. If you added or changed the class docstring, regenerate `docs/steps.md` by running `uv run scripts/generate_step_docs.py`.

### Choosing a base class

There are four base classes. Pick the narrowest one that fits your step.

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

**`ProtectStep`** — a specialization of `TextStep` for the common case of replacing a character with a placeholder token. You only implement `_pattern`, which returns a compiled regex with **exactly two capture groups** (what comes before and after the character being replaced). The `__call__` is fixed: it applies the pattern as `\1{placeholder}\2`.

```python
@register_step
class MyProtectStep(ProtectStep):
    name = "my_protect_step"
    placeholder = ProtectPlaceholder.MY_PLACEHOLDER

    def _pattern(self, operators: LanguageOperators) -> re.Pattern:
        return re.compile(r"(\d+)X(\d+)")  # two capture groups required
```

Use `ProtectStep` when: one regex pattern maps to exactly one placeholder substitution.

Use `TextStep` directly instead when: a single pass must protect two different symbols (like email `@` and `.`), the replacement needs to absorb surrounding whitespace with `\s*`, or the replacement is a per-match function rather than a fixed template.

**`RestoreStep`** — a specialization of `TextStep` for restoring a placeholder back to a string. You only implement `_replacement`, which returns the string to substitute in. The `__call__` does a plain `str.replace` of the placeholder (and its case-folded form).

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

E2E tests validate the full pipeline (preset + language) against a CSV fixture. The test runner lives in `tests/e2e/normalization_test.py` and CSV files go in `tests/e2e/files/`.

**CSV format** — three columns, no quoting needed unless the value contains a comma:

```
input,expected,language
$1,000,000,1000000 dollars,en
hello world,hello world,fr
```

Each row is one test case. The `language` column must match a registered language code (or `default`).

**Registering a new CSV** — add a block to `normalization_test.py` following the existing pattern:

```python
_MY_PRESET_CSV = _FILES_DIR / "my-preset.csv"
_MY_PRESET_TESTS = _load_tests_from_csv(_MY_PRESET_CSV) if _MY_PRESET_CSV.exists() else []
_MY_PRESET_PIPELINES: dict[str, NormalizationPipeline] = {}


@pytest.mark.parametrize(
    "test",
    _MY_PRESET_TESTS,
    ids=_case_ids(_MY_PRESET_TESTS),
)
def test_my_preset(test: NormalizationTest) -> None:
    pipeline = _load_pipeline("my-preset", test.language)
    result = pipeline.normalize(test.input)
    assert result == test.expected, (
        f"\n  input:    {test.input!r}"
        f"\n  expected: {test.expected!r}"
        f"\n  got:      {result!r}"
    )
```

Pipelines are cached per language inside `_MY_PRESET_PIPELINES` to avoid reloading for each parametrized case — follow the `_load_pipeline` helper pattern already in the file.

Steps must be **language-agnostic** — delegate all language-specific logic to the `operators` argument or read data from `operators.config.*`.

## Adding a new language

1. Create `normalization/languages/{lang}/` with `operators.py`, `replacements.py`, and `__init__.py`.
2. Put all word-level substitutions in `replacements.py`.
3. Instantiate a `LanguageConfig` and subclass `LanguageOperators` in `operators.py`.
4. Decorate with `@register_language` and add one import to `normalization/languages/__init__.py`.
5. Add tests under `tests/unit/languages/` and e2e fixture rows in `tests/e2e/files/`.

## Key design rules

- **Data vs. behavior**: if only the _values_ change by language, put them in `LanguageConfig`. If the _algorithm_ changes, override a method in `LanguageOperators`.
- **Presets are immutable**: never modify a published preset YAML — new behavior means a new preset file.
- **Placeholder pairs**: every `protect_*` step in Stage 1 must have a matching `restore_*` in Stage 3. The pipeline validates this at load time.
