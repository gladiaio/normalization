from . import (
    dutch,
    english,
    finnish,
    french,
    german,
    italian,
    norwegian,
    spanish,
    swedish,
)
from .base import LanguageOperators
from .registry import get_language_registry, register_language

register_language(LanguageOperators)

__all__ = [
    "dutch",
    "english",
    "finnish",
    "french",
    "german",
    "italian",
    "norwegian",
    "spanish",
    "swedish",
    "get_language_registry",
]
