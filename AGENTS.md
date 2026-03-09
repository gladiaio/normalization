# text_normalizers — Agent Guidelines

This document describes the architecture, conventions, and rules for contributing to `normalization`. Read it fully before making any change.

---

## What this project is

A Python library for normalizing speech-to-text transcription output and ground truth to enable fair Word Error Rate (WER) comparison across STT engines. It converts surface-form variations (currency symbols, written numbers, abbreviations, punctuation, fillers) into a canonical text representation so that semantically equivalent transcriptions are treated as identical.
The repository is using uv as package manager.

---

## Architecture overview

The pipeline has exactly three stages, always in this order:

1. **Text pre-processing** — full-text transformations before word splitting (e.g. placeholder protection, symbol conversion, contraction expansion)
2. **Word processing** — per-token transformations after splitting on spaces (e.g. replacements, email detection)
3. **Text post-processing** — full-text cleanup after rejoining words (e.g. placeholder restoration, digit collapsing)

This 3-stage structure is a hard constraint, not a suggestion. Steps have implicit ordering dependencies (a placeholder must be protected before symbols are removed, and restored after). Never flatten stages or allow steps to run out of order.

### Stage responsibilities

**text_pre_steps** — full text before word splitting.
Protect patterns (decimals, email symbols, slashes), expand multi-word forms (contractions, numbers, acronyms), convert symbols to words (currency, degrees, operators), apply character-level transforms (casefold, diacritics, punctuation removal), normalize whitespace.

**word_steps** — individual tokens after splitting, no neighbor context.
Skip special tokens (emails), apply single-word replacements (`vs` → `versus`), remove bracketed noise (`[inaudible]`).

**text_post_steps** — full text after word joining.
Restore placeholders to their final form (characters or words), format multi-word patterns (time, numbers), collapse digit sequences, normalize whitespace.

Pipelines are defined in YAML. The YAML lists which steps run in each stage. Step classes register themselves automatically via a decorator — the YAML name maps directly to the registered step.

---

## Project structure — key rules

### `languages/`

Each supported language is a **self-contained folder** (e.g. `languages/english/`). Every language folder follows the same structure:

- `operators.py` — subclass of `LanguageOperators`, holds the language config instance and any language-specific _behavioral_ method overrides
- `replacements.py` — a plain `dict[str, str]` of **all** word-level substitutions for this language. Every word replacement goes here — never add inline entries in `operators.py`. An empty dict is valid for languages with no replacements yet.
- `__init__.py` — exports the operators class and the replacements dict, nothing else. Do not re-export sentence replacements, number normalizers, or any other internal symbols.

**`languages/base/`** is a package that defines the full language contract. It contains two files:

- `language_config.py` — `LanguageConfig` dataclass: all language-specific _data_ (separators, currency words, filler words, digit words, time word maps, sentence replacements, etc.). Most fields have sensible defaults (empty dicts/lists, `None` for optional fields); steps that read them skip gracefully when `None`.
- `language_operator.py` — `LanguageOperators`: the base class and language-neutral fallback. Directly instantiable with no arguments — uses a minimal `LanguageConfig(code="default")` with empty symbol/currency mappings and all optional fields set to `None`. Registered in the language registry under `"default"` so it serves as the automatic fallback when no language is specified or the language is unsupported. All methods are no-ops. Only methods where the algorithm itself varies by language should be overridden in subclasses. Methods that are purely data-driven (i.e. the step owns the algorithm and only reads config values) do **not** belong here.

Both symbols are re-exported from `languages/base/__init__.py`.

Additional files beyond the required three (e.g. `number_normalizer.py`, `sentence_replacements.py`) are allowed when a language needs them, but they must never be empty. Number-related _data_ (digit words, number words) belongs in `LanguageConfig`. Only create a `number_normalizer.py` when the expansion _algorithm_ is complex enough to warrant its own module (see `languages/english/number_normalizer.py`).

When adding a new language:

1. Create a new folder under `languages/` with `operators.py`, `replacements.py`, and `__init__.py`
2. Decorate the operators class with `@register_language` — registration is automatic
3. Add one import line to `languages/__init__.py` to trigger the decorator at import time

### `steps/`

Steps are **atomic, stateless, single-responsibility** transformations. Each step class:

- Has a `name` class attribute (the string used in YAML)
- Is decorated with `@register_step` — this auto-registers it, no manual registry update needed
- Receives `(text, operators)` for text steps, or `(word, operators)` for word steps
- **Owns the algorithm** — the `__call__` method contains the transformation logic
- **Reads data from `operators.config.*`** — never hardcodes language-specific values

Steps are organized into `steps/text/` and `steps/word/` by stage. Protect/restore placeholder pairs always live in the **same file** (`steps/text/placeholders.py`) to keep their dependency explicit and co-located.

When adding a new step:

1. Create or add to the appropriate file under `steps/text/` or `steps/word/`
2. Decorate with `@register_step`
3. Add one import line to `steps/text/__init__.py` or `steps/word/__init__.py`
4. Add the step name to the relevant YAML preset(s) if it should run by default

### `pipeline/`

- `base.py` — `NormalizationPipeline`: the orchestrator. Holds the three ordered step lists, runs them, exposes `.describe()` and `.validate()`.
- `loader.py` — reads a YAML preset, resolves step names from the step registry, instantiates operators from the language registry, returns a ready-to-use pipeline.
- `replacer.py` — stateful compiled-regex engine used by the word replacement step. Lives here because it is infrastructure, not a step itself.

### `presets/`

Versioned YAML files shipped with the library. **Once published, a preset must never be modified** — benchmark reproducibility depends on it. New behavior means a new preset file with a new version name.

---

## Core conventions

### Auto-registration, not manual registries

Never manually maintain a dict mapping names to classes. Use the `@register_step` and `@register_language` decorators defined in `steps/registery.py` and `languages/registery.py`. The only manual work is adding an import line to the relevant `__init__.py` so the decorator runs at import time.

### Language data vs. language behavior

This is the central design rule. There are two distinct places for language-specific things:

**`LanguageConfig` (data)** — everything that can be expressed as a value: strings, lists, dicts. This includes separator characters, currency words, filler words, digit words, number words, and data-driven mappings like `time_words`, `sentence_replacements`, etc. Optional fields use `TypeAlias | None = None`; a `None` value means the step that reads it must skip gracefully. Semantic `TypeAlias` definitions (`TimeWords`, `DigitWords`, `SentenceReplacements`, etc.) are defined in `language_config.py` to make the contract self-documenting.

**`LanguageOperators` (behavior)** — only methods where the _algorithm itself_ varies by language. Examples: `expand_contractions` (uses an external library + custom regexes), `expand_written_numbers` (English uses a complex Whisper-derived normalizer), `normalize_numeric_time_formats` (am/pm regex structure), `fix_one_word_in_numeric_contexts` (language-specific digit-adjacent pattern), `get_compound_minutes` (English combines tens+ones with hyphen/space; other languages form these differently or not at all). If the algorithm is generic and only the _data_ differs, the data goes in `LanguageConfig` and the algorithm goes in the step — not in the operator.

Decision rule: ask "does the _logic_ change by language, or just the _values_?" If only values change → `LanguageConfig`. If the logic changes → `LanguageOperators` method override.

### Placeholder protection is ordered and paired

Any step that protects a character with a placeholder token must have a corresponding restore step. These must always be in `steps/text/placeholders.py`. The protect step must run in Stage 1 before `RemoveSymbolsStep`. The restore step must run in Stage 3. `pipeline.validate()` enforces this — do not bypass it. `loader.py` calls `validate()` automatically after constructing the pipeline.

When implementing placeholder steps, use the base classes where they fit:

- **`ProtectStep`** — use when the pattern has exactly two capture groups and emits a single placeholder (template: `\1{placeholder}\2`). Implement `_pattern(operators)`.
- **`RestoreStep`** — use when restoration is a plain string replacement of a single placeholder. Implement `_replacement(operators)`.
- **`TextStep`** directly — use when neither contract fits (multiple placeholders in one pass, zero-width patterns, per-match fan-out, marker deletion, post-replace logic). In that case, document why in the class docstring.

### Steps are language-agnostic

A step must not contain any language-specific logic or string literals. If the algorithm differs by language, add a method to `LanguageOperators` (with a no-op default in the base) and call `operators.that_method(text)` from the step. If only data differs, read it from `operators.config.*`. English-only helpers (e.g. `EnglishNumberNormalizer`) live inside `languages/english/`, not in `steps/`.

### Language folders are self-contained

Everything specific to a language lives inside its folder. If you find yourself adding a helper that only one language uses, it goes in that language's folder as an additional file — not in `steps/`, not in `pipeline/`. The English number normalizer (`languages/english/number_normalizer.py`) is the canonical example of this pattern.

### Presets are the reproducibility contract

Never modify a published preset YAML. Never let a preset reference a step that has changed its behavior under the same name. If a step's behavior changes, create a new step with a new name and update the relevant presets accordingly.

---

## Adding a new language — checklist

- [ ] Create `languages/{lang}/` with `operators.py`, `replacements.py`, `__init__.py`
- [ ] Put all word-level substitutions in `replacements.py`; do not add inline entries in `operators.py`
- [ ] Instantiate a `LanguageConfig` in `operators.py`, filling in all required fields and any optional dict fields your language needs (`time_words`, `sentence_replacements`, etc.)
- [ ] Subclass `LanguageOperators`, overriding only methods where the _algorithm_ differs (not just the data)
- [ ] If the language has digit words, populate `digit_words` in `LanguageConfig`
- [ ] If the language uses spoken time patterns, populate `time_words` with all needed word→digit mappings (clock hours 1-12 and minute-worth values up to 50); if it also uses compound minute expressions (e.g. "twenty-one"), override `get_compound_minutes()` to generate them — do **not** put this in config
- [ ] If number expansion is needed and the algorithm is complex, implement it in a `number_normalizer.py` file and override `expand_written_numbers`; otherwise do not create the file
- [ ] Decorate the class with `@register_language`
- [ ] Add one import to `languages/__init__.py`
- [ ] Add tests in `tests/unit/languages/`
- [ ] Add test rows to `tests/e2e/files/` for the new language

## Adding a new step — checklist

- [ ] Add the class to the appropriate file in `steps/text/` or `steps/word/`
- [ ] Set a unique `name` class attribute
- [ ] Decorate with `@register_step`
- [ ] Add one import to `steps/text/__init__.py` or `steps/word/__init__.py`
- [ ] Place the algorithm in `__call__`; read language data from `operators.config.*`; call operator methods only for genuinely behavioral differences
- [ ] If the step reads an optional `LanguageConfig` field, guard with `if operators.config.field is None: return text` and add a TODO comment
- [ ] Add unit tests in `tests/unit/steps/`
- [ ] If it involves placeholder protection, add both protect and restore to `steps/text/placeholders.py` and update `pipeline/base.py`'s `validate()` accordingly; use `ProtectStep`/`RestoreStep` base classes where the contract fits, otherwise use `TextStep` directly and document why in the docstring
- [ ] Add the step name to relevant preset YAMLs if needed (new preset version if existing presets are affected)
