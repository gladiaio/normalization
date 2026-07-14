# Getting started

## Install


=== "uv"

    ```bash
    uv add gladia-normalization
    ```

=== "pip"

    ```bash
    pip install gladia-normalization
    ```

=== "From source"

    ```bash
    git clone https://github.com/gladiaio/normalization.git
    cd normalization
    uv sync
    ```

Requires **Python 3.10+**.

## Normalize text

```python
from normalization import load_pipeline

pipeline = load_pipeline("gladia-3", language="en")
print(pipeline.normalize("It's $50 at 3:00PM"))
# it is 50 dollars at 3 pm
```

- First argument: built-in preset name (`"gladia-3"`) or path to a YAML file
- Second argument: language code (`"en"`, `"fr"`, …) — see [Languages](languages.md)

## CLI

```bash
gladia-normalization "A tea cost £2 at 3:30PM" --language en
```

Or without installing permanently:

```bash
uvx gladia-normalization "A tea cost £2 at 3:30PM" --language en
```

More options in the [CLI reference](usage/cli.md).

## Next steps

- [Python API](usage/python.md) — `describe()`, custom presets
- [How it works](concepts.md) — three-stage pipeline
- [Step reference](reference/steps.md) — every available step
