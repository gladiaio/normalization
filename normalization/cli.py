import argparse
import json
import sys

from normalization import load_pipeline
from normalization.languages import get_language_registry
from normalization.pipeline.loader import _PRESETS_DIR


def _available_languages() -> list[str]:
    import normalization.languages  # noqa: F401 — triggers @register_language decorators

    return sorted(get_language_registry().keys())


def _available_presets() -> list[str]:
    return sorted(p.stem for p in _PRESETS_DIR.glob("*.yaml"))


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="normalize",
        description="Normalize STT transcription text for fair WER comparison.",
    )
    parser.add_argument(
        "text",
        nargs="?",
        help="Text to normalize. Reads from stdin if omitted.",
    )
    parser.add_argument(
        "--language",
        "-l",
        default="en",
        metavar="CODE",
        help="Language code (default: en). Available: %(choices)s.",
        choices=_available_languages(),
    )
    parser.add_argument(
        "--preset",
        "-p",
        default="gladia-3",
        metavar="PRESET",
        help="Built-in preset name or path to a YAML file (default: gladia-3).",
    )
    parser.add_argument(
        "--describe",
        action="store_true",
        help="Print the pipeline description as JSON and exit.",
    )

    args = parser.parse_args()

    try:
        pipeline = load_pipeline(args.preset, args.language)
    except FileNotFoundError as exc:
        parser.error(str(exc))

    if args.describe:
        print(json.dumps(pipeline.describe(), indent=2))
        return

    if args.text is not None:
        text = args.text
    elif not sys.stdin.isatty():
        text = sys.stdin.read().strip()
    else:
        parser.error("Provide text as an argument or pipe it via stdin.")

    print(pipeline.normalize(text))


if __name__ == "__main__":
    main()
