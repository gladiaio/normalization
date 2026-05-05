from . import dutch, english, finnish, french, german, italian, spanish, swedish
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
    "swedish",
    "get_language_registry",
]
