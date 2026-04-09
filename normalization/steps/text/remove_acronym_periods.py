import re

from normalization.languages.base import LanguageOperators
from normalization.steps.base import TextStep
from normalization.steps.registry import register_step


@register_step
class RemoveAcronymPeriodsStep(TextStep):
    """Remove periods from acronyms (U.S.A. -> USA, U.S. -> US)."""

    name = "remove_acronym_periods"

    def __call__(self, text: str, operators: LanguageOperators) -> str:
        text = re.sub(r"\b([A-Z])\.([A-Z])\.([A-Z])\.", r"\1\2\3", text)
        text = re.sub(r"\b([A-Z])\.([A-Z])\.", r"\1\2", text)
        return text
