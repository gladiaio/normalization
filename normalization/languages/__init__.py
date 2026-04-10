from . import english, french, german, italian
from .base import LanguageOperators
from .registry import get_language_registry, register_language

register_language(LanguageOperators)

__all__ = ["english", "french", "german", "italian", "get_language_registry"]
