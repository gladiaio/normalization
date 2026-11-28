# Presets

A preset declares which steps run in each stage and in what order.

## Built-in

| Name | Package path | What it adds |
| --- | --- | --- |
| `gladia-3` | `normalization/presets/gladia-3.yaml` | The preset behind Gladia's published WER figures |
| `gladia-4` | `normalization/presets/gladia-4.yaml` | `gladia-3`, plus digit and spelled ordinals normalized to the same form (`premier` and `1re` → `1er`) |

```python
load_pipeline("gladia-3", language="en")
```

### `gladia-4`

`gladia-4` is `gladia-3` with ordinals normalized alike, whether written with digits or spelled out. As in English (`first` and `1st` both give `1st`), both forms become the digits plus one suffix per language, glued to the digits:

| Language | Canonical form | Example |
| --- | --- | --- |
| French | `1er`, then `2e`, `3e`, … | `premier`, `première`, `1re`, `1ère` → `1er`; `deuxième`, `2ème`, `2nd` → `2e` |
| Danish, Norwegian, German | `1.` | `første`, `1ste`, `1.` → `1.`; `ersten`, `1ten`, `1.` → `1.` |
| Swedish | `1:a` | `första`, `1:a` → `1:a`; `tredje`, `3:e` → `3:a` |
| Dutch | `1e` | `eerste`, `1ste`, `1e` → `1e` |
| Spanish, Italian, Portuguese | `1º` (masculine and feminine) | `primero`, `primera`, `1º`, `1.º`, `1ª` → `1º` |

An ordinal is never a bare number, so it is not glued to a number next to it: da `den første 2 maj` gives `den 1. 2 maj` (`gladia-3`: `den 12 maj`).

| Language | Input | `gladia-3` | `gladia-4` |
| --- | --- | --- | --- |
| fr | `le premier mai` | `le premier mai` | `le 1er mai` |
| fr | `le 1er mai` | `le 1 e r mai` | `le 1er mai` |
| fr | `au 3e étage` | `au 3 e etage` | `au 3e etage` |
| da | `den første 2 maj` | `den 12 maj` | `den 1. 2 maj` |
| de | `am 1ten Mai` | `am 1 t e n mai` | `am 1. mai` |
| sv | `den 1:a maj` | `den 1 a maj` | `den 1:a maj` |
| nl | `de 1ste mei` | `de 1 is het e mei` | `de 1e mei` |
| es | `el 1.º de mayo` | `el 1 o de mayo` | `el 1º de mayo` |

Words that are also something else stay words: sv `andra` and no `andre` (also "other"), fr `seconde`, es `segundo` and `cuarto`, it `secondo` and `prima`, pt `segundo` and `segunda`, de `Erstens`. A number followed by a period is read as an ordinal in Danish, Norwegian and German only when another word follows it (`am 1. Mai`), not at the end of the text (`Ich habe 3.` → `ich habe 3`). Ordinals in other languages, and every other output, are the same as `gladia-3`.

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
