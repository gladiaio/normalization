from typing import Type

from normalization.steps.base import TextStep, WordStep

_STEP_REGISTRY: dict[str, dict[str, Type[TextStep] | Type[WordStep]]] = {
    "text": {},
    "word": {},
}


def register_step(cls):
    """Decorator that auto-registers a step class by its `name` attribute."""
    assert hasattr(cls, "name"), f"{cls} must define a `name` class attribute"

    # Determine step type based on module path
    step_type = "text" if ".text." in cls.__module__ else "word"

    assert cls.name not in _STEP_REGISTRY[step_type], (
        f"Step name '{cls.name}' is already registered in {step_type}"
    )
    _STEP_REGISTRY[step_type][cls.name] = cls
    return cls


def get_step_registry() -> dict[str, dict[str, Type[TextStep] | Type[WordStep]]]:
    return _STEP_REGISTRY
