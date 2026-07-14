# Contributing

Bug reports, new steps, and new languages are welcome. Setup and where to start are below. Check [Contributor guide](guide.md) for design rules.

## Setup

```bash
git clone https://github.com/gladiaio/normalization.git
cd normalization
uv sync --all-groups
uv run pre-commit install --install-hooks
```

## Checks

```bash
uv run pytest
uv run ruff check .
uv run ruff format .
uv run ty check
```

## Docs site (this site)

```bash
uv sync --group docs
uv run mkdocs serve   # http://127.0.0.1:8000
uv run mkdocs build
```

## How to help

| Contribution | Start here                                             |
| ------------ | ------------------------------------------------------ |
| New language | [Checklist](guide.md#adding-a-new-language-checklist)  |
| New step     | [Checklist](guide.md#adding-a-new-step-checklist)      |
| Bug report   | GitHub issue with reproduce steps + expected vs actual |
| Question     | GitHub issue with the `question` label                 |

Also see [`CONTRIBUTING.md`](https://github.com/gladiaio/normalization/blob/main/CONTRIBUTING.md) for PR workflow and commit style.
