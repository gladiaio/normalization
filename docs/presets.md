# Presets

A preset declares which steps run in each stage and in what order.

## Built-in

| Name | Package path |
| --- | --- |
| `gladia-3` | `normalization/presets/gladia-3.yaml` |

```python
load_pipeline("gladia-3", language="en")
```

## Custom preset

```yaml
name: my-preset-v1

stages:
  text_pre:
    - protect_email_symbols
    - expand_contractions
    - casefold_text
    - remove_symbols
    - remove_diacritics

  word:
    - apply_word_replacements

  text_post:
    - restore_email_at_symbol_with_word
    - restore_email_dot_symbol_with_word
```

```python
from normalization import load_pipeline

pipeline = load_pipeline("path/to/my-preset.yaml", language="en")
```

## Rules

- Step names must match a registered step's `name` attribute — see [Step reference](reference/steps.md)
- List order = execution order
- Every `protect_*` in `text_pre` needs a matching `restore_*` in `text_post` (validated at load)
- **Published presets are immutable** — change behavior by shipping a new versioned file, never by editing an existing one
