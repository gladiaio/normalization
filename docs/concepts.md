# How it works

Every pipeline runs **three stages**, always in this order:

```text
text  ──►  [1] text_pre  ──►  split  ──►  [2] word  ──►  join  ──►  [3] text_post  ──►  text
```

| Stage | Operates on | Typical work |
| --- | --- | --- |
| **1. Text pre** | Full string | Protect symbols, expand contractions/numbers, convert currency/degrees, casefold, remove punctuation |
| **2. Word** | One token | Replacements (`vs` → `versus`), skip emails |
| **3. Text post** | Full string | Restore placeholders, format times, collapse digits, whitespace |

This order is a hard constraint. Placeholder steps illustrate why: a decimal point is **protected** in stage 1 so `remove_symbols` cannot erase it, then **restored** in stage 3.

## Steps

A step is a small, stateless transform with a unique `name`. Steps register themselves via `@register_step`; presets reference those names.

See the full [step reference](reference/steps.md).

## Presets

A preset is a YAML file that lists which steps run in each stage and in what order. Published presets are **immutable** — new behavior means a new preset file (e.g. `gladia-4`).

Details and custom YAML: [Presets](presets.md).

## Languages

Language-specific data and behavior live under `normalization/languages/`. Unknown codes fall back to a language-agnostic default.

Details: [Languages](languages.md).
