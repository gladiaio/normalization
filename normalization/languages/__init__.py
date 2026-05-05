from . import dutch, english, finnish, french, german, italian, spanish
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
    "spanish",
    "get_language_registry",
]
