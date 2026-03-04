from typing import Protocol

from normalization.languages.base import LanguageOperators


class TextStep(Protocol):
    """A transformation applied to the full text string."""

    name: str

    def __call__(self, text: str, operators: LanguageOperators) -> str: ...
