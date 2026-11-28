# Presets

A preset declares which steps run in each stage and in what order.

## Built-in

| Name | Package path | What it adds |
| --- | --- | --- |
| `gladia-3` | `normalization/presets/gladia-3.yaml` | The preset behind Gladia's published WER figures |
| `gladia-4` | `normalization/presets/gladia-4.yaml` | `gladia-3`, plus digit and spelled ordinals normalized to the same form |

```python
load_pipeline("gladia-3", language="en")
```

### `gladia-4`

`gladia-4` is `gladia-3` with ordinals normalized alike, whether written with digits or spelled out:

- a digit ordinal loses its suffix (`1er`, `1ste`, `1:a`, `1º` → `1`) instead of being spelled out letter by letter;
- a spelled ordinal becomes its number (`premier`, `ersten`, `primero` → `1`);
- an ordinal stays apart from a number next to it (da `den første 2 maj` → `den 1 2 maj`, not `den 12 maj`).

Languages: Danish, Dutch, French, German, Italian, Norwegian, Portuguese, Spanish and Swedish. English keeps `1st` for both `first` and `1st`. Every other output is the same as `gladia-3`.

| Language | Input | `gladia-3` | `gladia-4` |
| --- | --- | --- | --- |
| fr | `le 1er mai` | `le 1 e r mai` | `le 1 mai` |
| nl | `de 1ste mei` | `de 1 is het e mei` | `de 1 mei` |
| da | `den første 2 maj` | `den 12 maj` | `den 1 2 maj` |

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
