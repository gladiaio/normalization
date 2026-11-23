from . import (
    arabic,
    danish,
    dutch,
    english,
    finnish,
    french,
    german,
    italian,
    norwegian,
    portuguese,
    romanian,
    russian,
    spanish,
    swedish,
)
from .base import LanguageOperators
from .registry import get_language_registry, register_language

register_language(LanguageOperators)

__all__ = [
    "arabic",
    "danish",
    "dutch",
    "english",
    "finnish",
    "french",
    "german",
    "italian",
    "norwegian",
    "portuguese",
    "romanian",
    "russian",
    "spanish",
    "swedish",
    "get_language_registry",
]
