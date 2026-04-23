from . import dutch, english, french, german, italian, norwegian, spanish
from .base import LanguageOperators
from .registry import get_language_registry, register_language

register_language(LanguageOperators)

__all__ = [
    "dutch",
    "english",
    "french",
    "german",
    "italian",
    "norwegian",
    "spanish",
    "get_language_registry",
]
