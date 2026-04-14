from . import english, french, german, italian, spanish
from .base import LanguageOperators
from .registry import get_language_registry, register_language

register_language(LanguageOperators)

__all__ = ["english", "french", "german", "italian", "spanish", "get_language_registry"]
