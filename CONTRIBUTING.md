# Contributing to gladia-normalization

Thanks for your interest in contributing! Every contribution — whether it's a new language, a normalization step, or a bug report — makes the library more useful for the entire voice AI community.

## Code of conduct

Please be respectful and welcoming in all interactions. We're committed to making this a safe and inclusive space for everyone. If you experience or witness unacceptable behavior, please open a GitHub issue or contact the maintainers directly.

## How you can help

### Add support for a new language

This is the most impactful contribution. We don't master every language — and that's exactly where the community can make a difference. If you speak a language not yet supported, you can add it in a self-contained folder with no changes to the core pipeline.

A new language requires:

1. Create `normalization/languages/{lang}/` with `operators.py`, `replacements.py`, and `__init__.py`
2. Put all word-level substitutions in `replacements.py`
3. Instantiate a `LanguageConfig` and subclass `LanguageOperators` in `operators.py`
4. Decorate with `@register_language` and add one import to `normalization/languages/__init__.py`
5. Add tests under `tests/unit/languages/` and e2e fixture rows in `tests/e2e/files/`

See [docs/contributing-guide.md](docs/contributing-guide.md) for the full checklist and design rules.

### Add a new normalization step

Steps are atomic, stateless transformations that plug into the pipeline via a decorator — no manual registry updates needed.

A new step requires:

1. Create or extend a file under `normalization/steps/text/` or `normalization/steps/word/`
2. Decorate the class with `@register_step` and set a unique `name` attribute
3. Add an import to `steps/text/__init__.py` or `steps/word/__init__.py`
4. Add unit tests under `tests/unit/steps/`
5. Add the step name to the relevant preset YAML, or create a new preset version
6. If you added or changed the class docstring, regenerate `docs/steps.md`: `uv run scripts/generate_step_docs.py`

See [docs/contributing-guide.md](docs/contributing-guide.md) for base class selection and test conventions.

### Report a bug

Open an issue with steps to reproduce, expected vs. actual behavior, and your environment (Python version, OS, package version).

### Ask a question

Open a GitHub issue with the `question` label. We're happy to help.

---

## Development setup

```bash
git clone https://github.com/gladiaio/normalization.git
cd normalization
uv sync
uv run pre-commit install --install-hooks   # install hooks once
```

Run the checks at any time:

```bash
uv run pytest               # run tests
uv run ruff check .         # lint
uv run ruff format .        # format
uv run ty check             # type-check
```

---

## Submitting changes

1. Fork the repo and create a branch: `git checkout -b feat/my-feature`
2. Make your changes and add tests
3. Run the checks (see above) and make sure everything passes
4. Push your branch: `git push origin your-feature-branch`
5. Open a pull request on GitHub with a clear description of your changes, filling the [template](./.github/pull_request_template.md)
6. Address review feedback and push updates
7. Once approved, your PR will be merged

### Pre-commit hooks

The hooks run automatically on every commit: Ruff (lint + format), ty (type-check), and commit message validation. If a hook fails, fix the issue and commit again.

## Commit style

We use [Conventional Commits](https://www.conventionalcommits.org/): prefix your commit with `feat:`, `fix:`, `docs:`, `chore:`, etc.
