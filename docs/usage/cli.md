# CLI

Installed as `gladia-normalization` (entry point from the package).

## Examples

```bash
# Single string
gladia-normalization "A tea cost £2 at 3:30PM" --language en

# File
gladia-normalization --file transcript.txt --language en

# Stdin
echo "A tea cost £2 at 3:30PM" | gladia-normalization --language fr

# Custom preset
gladia-normalization "..." --preset path/to/my-preset.yaml --language en

# Inspect pipeline (JSON)
gladia-normalization --describe --language en
```

Without a permanent install:

```bash
uvx gladia-normalization "A tea cost £2 at 3:30PM" --language en
```

## Options

| Flag | Default | Description |
| --- | --- | --- |
| `text` | — | Positional text to normalize (or use stdin / `--file`) |
| `-l`, `--language` | `en` | Language code |
| `-p`, `--preset` | `gladia-3` | Built-in preset name or YAML path |
| `-f`, `--file` | — | Read input from a file (mutually exclusive with positional text) |
| `--describe` | — | Print pipeline description as JSON and exit |

Provide either positional text or `--file`, not both.
