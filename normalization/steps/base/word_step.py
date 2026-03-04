from typing import Protocol

from normalization.languages.base import LanguageOperators


class WordStep(Protocol):
    """A transformation applied to a single word token."""

    name: str

    def __call__(self, word: str, operators: LanguageOperators) -> str: ...
