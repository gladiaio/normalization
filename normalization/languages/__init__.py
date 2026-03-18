from . import dutch, english, french
from .base import LanguageOperators
from .registery import get_language_registry, register_language

register_language(LanguageOperators)

__all__ = ["dutch", "english", "french", "get_language_registry"]
