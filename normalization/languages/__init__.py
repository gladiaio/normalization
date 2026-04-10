# Registery before dutch/english/french so register_language exists when operators load.
from .base import LanguageOperators
from .registery import get_language_registry, register_language

register_language(LanguageOperators)

from . import dutch, english, french  # noqa: E402

__all__ = ["dutch", "english", "french", "get_language_registry"]
