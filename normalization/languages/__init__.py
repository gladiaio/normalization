from . import english, french
from .base import LanguageOperators
from .registry import get_language_registry, register_language

register_language(LanguageOperators)

__all__ = ["english", "french", "get_language_registry"]
