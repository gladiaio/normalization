# Languages

Pass a language code to `load_pipeline` or `--language`. Unknown codes fall back to a language-agnostic default (independent transforms only).

<div class="gladia-hero-center" markdown="1">
| Code | Language |
| --- | --- |
| `da` | Danish |
| `de` | German |
| `en` | English |
| `es` | Spanish |
| `fi` | Finnish |
| `fr` | French |
| `it` | Italian |
| `nl` | Dutch |
| `no` | Norwegian |
| `sv` | Swedish |
</div>

## What "language-aware" means

Each language folder under `normalization/languages/` provides:

- **Config data** — currency words, fillers, digit words, time maps, etc. (`LanguageConfig`)
- **Behavior overrides** — only when the algorithm itself differs (e.g. number expansion)
- **Word replacements** — a plain dict in `replacements.py`

Steps stay language-agnostic: they read `operators.config.*` or call operator methods.

## Adding a language

See the [contributor guide](contributing/guide.md#adding-a-new-language-checklist).
