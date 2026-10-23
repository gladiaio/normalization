from . import (
    danish,
    dutch,
    english,
    finnish,
    french,
    german,
    italian,
    norwegian,
    portuguese,
    spanish,
    swedish,
)
from .base import LanguageOperators
from .registry import get_language_registry, register_language

register_language(LanguageOperators)

__all__ = [
    "danish",
    "dutch",
    "english",
    "finnish",
    "french",
    "german",
    "italian",
    "norwegian",
    "portuguese",
    "spanish",
    "swedish",
    "get_language_registry",
]
