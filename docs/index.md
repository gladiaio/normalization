<p class="gladia-eyebrow" markdown="0">Open source · STT · WER</p>

# Normalization

<p class="gladia-lead">
Normalize speech-to-text transcripts before computing Word Error Rate, so formatting differences stop looking like recognition errors.
</p>

<div class="gladia-hero-center" markdown="1">

| Ground truth | STT output | Without normalization |
| --- | --- | --- |
| It's $50 | it is fifty dollars | treated as errors |
| 3:00 PM | 3 pm | treated as errors |
| Mr. Smith | mister smith | treated as errors |

```text
Input:  "It's $50.9 at 3:00PM — y'know, roughly."
Output: "it is 50 point 9 dollars at 3 pm you know roughly"
```

[Get started](getting-started.md){ .md-button .md-button--primary }
[How it works](concepts.md){ .md-button }

</div>

## Quick example

```python
from normalization import load_pipeline

pipeline = load_pipeline("gladia-3", language="en")
pipeline.normalize("It's $50 at 3:00PM")
# => "it is 50 dollars at 3 pm"
```

```bash
pip install gladia-normalization
gladia-normalization "It's $50 at 3:00PM" --language en
```

## What you get

- **Deterministic presets** — same YAML preset → same output every time
- **Language-aware** — [supported languages](languages.md) with a safe fallback for others
- **Composable steps** — build custom pipelines without forking the core
- **Inspectable** — `pipeline.describe()` shows exactly what will run

Continue with [Getting started](getting-started.md) or skim [How it works](concepts.md).
