"""Every configured filler word must actually be removed by the pipeline.

``remove_filler_words`` runs after ``remove_diacritics`` in gladia-3, so a
filler listed with a diacritic can only match because ``LanguageOperators``
folds the list with ``remove_diacritics`` when the operators are built. These
tests walk every language's filler list as it is written in the config and
assert each entry is removed, so a future entry that cannot match fails CI
instead of silently leaking into transcripts (issue #54).
"""

import pytest

from normalization.languages.arabic.operators import ARABIC_CONFIG
from normalization.languages.base import LanguageConfig
from normalization.languages.base.diacritics import remove_diacritics
from normalization.languages.danish.operators import DANISH_CONFIG
from normalization.languages.dutch.operators import DUTCH_CONFIG
from normalization.languages.english.operators import ENGLISH_CONFIG
from normalization.languages.finnish.operators import FINNISH_CONFIG
from normalization.languages.french.operators import FRENCH_CONFIG
from normalization.languages.german.operators import GERMAN_CONFIG
from normalization.languages.italian.operators import ITALIAN_CONFIG
from normalization.languages.norwegian.operators import NORWEGIAN_CONFIG
from normalization.languages.portuguese.operators import PORTUGUESE_CONFIG
from normalization.languages.registry import get_language_registry
from normalization.languages.romanian.operators import ROMANIAN_CONFIG
from normalization.languages.spanish.operators import SPANISH_CONFIG
from normalization.languages.swedish.operators import SWEDISH_CONFIG
from normalization.pipeline.loader import load_pipeline

# The module-level configs hold the filler words as contributors write them
# (natural, accented form); LanguageOperators folds a copy at build time and
# leaves these untouched.
_LANGUAGE_CONFIGS: list[LanguageConfig] = [
    ARABIC_CONFIG,
    DANISH_CONFIG,
    DUTCH_CONFIG,
    ENGLISH_CONFIG,
    FINNISH_CONFIG,
    FRENCH_CONFIG,
    GERMAN_CONFIG,
    ITALIAN_CONFIG,
    NORWEGIAN_CONFIG,
    PORTUGUESE_CONFIG,
    ROMANIAN_CONFIG,
    SPANISH_CONFIG,
    SWEDISH_CONFIG,
]


def _filler_entries() -> list[tuple[str, str]]:
    return [
        (config.code, filler)
        for config in _LANGUAGE_CONFIGS
        for filler in config.filler_words
    ]


def test_every_registered_language_is_covered() -> None:
    registered = set(get_language_registry()) - {"default"}
    assert registered == {config.code for config in _LANGUAGE_CONFIGS}


@pytest.mark.parametrize(("language", "filler"), _filler_entries())
def test_filler_entry_is_removed_by_pipeline(language: str, filler: str) -> None:
    """Feed each configured filler through the gladia-3 pipeline and assert removal.

    At filler-matching time the token reads ``remove_diacritics(filler)``; the
    trailing " 5" is a payload that must survive untouched.
    """
    pipeline = load_pipeline("gladia-3", language)
    result = pipeline.normalize(f"{filler} 5")
    assert result == "5", (
        f"[{language}] filler {filler!r} "
        f"(matches as {remove_diacritics(filler)!r}) was not removed: {result!r}"
    )


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        # The filler "öö" is removed (folded to "oo" at operator build time)...
        ("öö minä tiedän", "mina tiedan"),
        # ...but the genuine colloquial verb "oo" ("is/am") keeps mapping to
        # "ole": the replacement is keyed on the pre-diacritics form, which the
        # folded filler cannot take.
        ("se oo totta", "se ole totta"),
        ("hän oo täällä", "han ole taalla"),
    ],
)
def test_finnish_oo_verb_is_kept_and_oo_filler_removed(
    text: str, expected: str
) -> None:
    pipeline = load_pipeline("gladia-3", "fi")
    assert pipeline.normalize(text) == expected
