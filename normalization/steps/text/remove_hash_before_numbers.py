import re

from normalization.languages.base import LanguageOperators
from normalization.steps.base import TextStep
from normalization.steps.registery import register_step


@register_step
class RemoveHashBeforeNumbersStep(TextStep):
    """Remove # symbol before numbers (#1 -> 1)."""

    name = "remove_hash_before_numbers"

    def __call__(self, text: str, operators: LanguageOperators) -> str:
        return re.sub(r"#(\d+)", r"\1", text)
