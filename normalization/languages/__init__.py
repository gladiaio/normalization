from . import english, french, italian
from .base import LanguageOperators
from .registry import get_language_registry, register_language

register_language(LanguageOperators)

__all__ = ["english", "french", "italian", "get_language_registry"]
