<p align="center">
  <h1 align="center">Normalization</h1>
  <p align="center">
    Text normalization for fair speech-to-text evaluation.
    <br />
    <a href="#quick-start">Quick Start</a> &middot; <a href="docs/steps.md">Step Reference</a> &middot; <a href="#contributing">Contributing</a>
  </p>
</p>

<p align="center">
  <img src="https://img.shields.io/pypi/v/gladia-normalization?style=flat-square" alt="PyPI version" />
  <img src="https://img.shields.io/pypi/pyversions/gladia-normalization?style=flat-square" alt="Python versions" />
  <img src="https://img.shields.io/github/license/gladiaio/normalization?style=flat-square" alt="License" />
</p>

---

## Why normalization matters

Word Error Rate (WER) is the standard metric for evaluating speech-to-text systems. But WER operates on raw strings — it has no notion of meaning. Two transcriptions that say the same thing in different surface forms get penalized as errors:

| Ground truth | STT output          | Match without normalization |
| ------------ | ------------------- | --------------------------- |
| It's $50     | it is fifty dollars | 0/3 words match             |
| 3:00 PM      | 3 pm                | 0/2 words match             |
| Mr. Smith    | mister smith        | 0/2 words match             |

These aren't transcription errors — they're formatting differences. Without normalization, WER scores become unreliable and comparisons across engines are meaningless.

`gladia-normalization` solves this by reducing both the ground truth and the STT output to a shared canonical form _before_ WER is computed, so that only genuine recognition errors affect the score.

## What it does

The library runs your text through a configurable pipeline of normalization steps — expanding contractions, converting symbols to words, removing fillers, casefolding, and more — to produce a clean, canonical output.

```
Input:  "It's $50.9 at 3:00PM — y'know, roughly."
Output: "it is 50 point 9 dollars at 3 pm you know roughly"
```

The pipeline is deterministic, language-aware, and fully defined in YAML — run the same preset and get the same output every time.

## Quick start

### Installation

```bash
pip install gladia-normalization
```

<details>
<summary>Install from source</summary>

```bash
git clone https://github.com/gladiaio/normalization.git
cd normalization
uv sync
```

</details>

### Usage

```python
from normalization import load_pipeline

# Load a built-in preset by name
pipeline = load_pipeline("gladia-3", language="en")

pipeline.normalize("It's $50 at 3:00PM")
# => "it is 50 dollars at 3 pm"
```

## How it works

Every pipeline runs exactly **three stages**, always in this order:

- **Stage 1 — Text pre-processing**: Full-text transforms: protect symbols, expand contractions, convert numbers, casefold, remove symbols
- **Stage 2 — Word processing**: Per-token transforms: word replacements, filler removal
- **Stage 3 — Text post-processing**: Full-text cleanup: restore placeholders, collapse digits, format time patterns, normalize whitespace

This ordering is a hard constraint. Some steps depend on earlier steps having run (e.g. a placeholder protecting a decimal point in Stage 1 must be restored in Stage 3, so that `remove_symbols` doesn't destroy it in between).

Pipelines are defined declaratively in **YAML presets**. Each preset lists the steps that run in each stage and the order they run in. See the full [step reference](docs/steps.md) for every available step.

## Supported languages

| Code | Language       |
| ---- | -------------- |
| `en` | English        |
| `fr` | French (alpha) |

Unsupported language codes fall back to a safe default that applies language-independent normalization only.

Adding a new language is self-contained — create a folder, register it with a decorator, done. See [Contributing](#adding-a-new-language).

## Custom presets

A preset is a YAML file that declares which steps run in each stage and in what order.

```yaml
name: my-preset-v1

stages:
  text_pre:
    - protect_email_symbols
    - expand_contractions
    - casefold_text
    - remove_symbols
    - remove_diacritics
    - normalize_whitespace

  word:
    - apply_word_replacements

  text_post:
    - restore_email_at_symbol_with_word
    - restore_email_dot_symbol_with_word
    - normalize_whitespace
```

_Load from your custom configuration:_

```python
from normalization import load_pipeline

pipeline = load_pipeline("path/to/my-custom-configuration.yaml", language="en")
result = pipeline.normalize("some transcription text")
```

Inspect a loaded pipeline:

```python
pipeline.describe()
# {'name': 'my-preset-v1', 'language': 'en', 'text_pre_steps': [...], ...}
```

**Preset rules:**

- Step names must match the `name` attribute of a registered step class.
- Every `protect_*` step in `text_pre` requires a matching `restore_*` in `text_post`. The pipeline validates this at load time.
- List order is execution order.
- Published presets are immutable — new behavior means a new file.

## Contributing

### Adding a new step

1. Create or extend a file under `normalization/steps/text/` or `normalization/steps/word/`.
2. Decorate the class with `@register_step` and set a unique `name` attribute.
3. Add an import to `steps/text/__init__.py` or `steps/word/__init__.py`.
4. Add unit tests under `tests/unit/steps/`.
5. Add the step to the relevant preset YAML, or create a new preset version.

```python
from normalization.languages.base import LanguageOperators
from normalization.steps.base import TextStep
from normalization.steps.registery import register_step

@register_step
class MyNewStep(TextStep):
    name = "my_new_step"

    def __call__(self, text: str, operators: LanguageOperators) -> str:
        return operators.some_method(text)
```

Steps must be language-agnostic — delegate all language-specific logic to the `operators` argument.

### Adding a new language

1. Create `normalization/languages/{lang}/` with `operators.py`, `replacements.py`, and `__init__.py`.
2. Instantiate a `LanguageConfig` and subclass `LanguageOperators`.
3. Decorate with `@register_language` and add one import to `normalization/languages/__init__.py`.
4. Add tests under `tests/unit/languages/` and e2e fixture rows in `tests/e2e/`.

### Development

```bash
uv run pytest              # run tests
uv run ruff check .        # lint
uv run ruff format .       # format
uv run pyright             # type-check
```

## License

TBD
