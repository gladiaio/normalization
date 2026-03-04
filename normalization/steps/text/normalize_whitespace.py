import re

from normalization.languages.base import LanguageOperators
from normalization.steps.base import TextStep
from normalization.steps.registery import register_step


@register_step
class NormalizeWhitespaceStep(TextStep):
    """Collapse multiple spaces into one and strip leading/trailing whitespace."""

    name = "normalize_whitespace"

    def __call__(self, text: str, operators: LanguageOperators) -> str:
        return re.sub(r"\s+", " ", text).strip()
