import re

from normalization.languages.base import LanguageOperators
from normalization.steps.base import TextStep
from normalization.steps.registery import register_step


@register_step
class RemoveTrailingPeriodStep(TextStep):
    """Remove trailing period from text."""

    name = "remove_trailing_period"

    def __call__(self, text: str, operators: LanguageOperators) -> str:
        return re.sub(r"\s*\.\s*$", "", text)
