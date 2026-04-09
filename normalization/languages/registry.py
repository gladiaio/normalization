from typing import Any

_LANGUAGE_REGISTRY: dict[str, Any] = {}


def register_language(cls):
    """Decorator that auto-registers a language operators class by its config code."""
    instance = cls()
    assert instance.config.code not in _LANGUAGE_REGISTRY, (
        f"Language code '{instance.config.code}' is already registered"
    )
    _LANGUAGE_REGISTRY[instance.config.code] = cls
    return cls


def get_language_registry() -> dict[str, Any]:
    return _LANGUAGE_REGISTRY
