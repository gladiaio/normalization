# Python API

Public entry points:

```python
from normalization import load_pipeline, NormalizationPipeline
```

## `load_pipeline`

```python
load_pipeline(preset: str | Path, language: str) -> NormalizationPipeline
```

| Argument | Meaning |
| --- | --- |
| `preset` | Built-in name (`"gladia-3"`) or path to a YAML file |
| `language` | Language code (`"en"`, `"fr"`, …). Unknown codes use the safe default |

Raises `FileNotFoundError` if the preset cannot be resolved. Validates protect/restore pairing at load time.

## `NormalizationPipeline.normalize`

```python
pipeline.normalize(text: str) -> str
```

Runs all three stages and returns the normalized string.

```python
pipeline = load_pipeline("gladia-3", language="en")
pipeline.normalize("Mr. Smith paid $1,000")
# => "mister smith paid 1000 dollars"
```

## Inspect a pipeline

```python
pipeline.describe()
# {
#   "name": "gladia-3",
#   "language": "en",
#   "text_pre_steps": [...],
#   "word_steps": [...],
#   "text_post_steps": [...],
# }
```

## Custom preset file

```python
pipeline = load_pipeline("path/to/my-preset.yaml", language="fr")
result = pipeline.normalize("Bonjour — ça coûte 50€")
```

Preset format: [Presets](../presets.md).
