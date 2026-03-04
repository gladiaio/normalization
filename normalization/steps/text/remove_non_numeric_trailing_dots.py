import re

from normalization.languages.base import LanguageOperators
from normalization.steps.base import TextStep
from normalization.steps.registery import register_step


@register_step
class RemoveNonNumericTrailingDotsStep(TextStep):
    """Remove dots that are not between digits (.X -> ' X', trailing .)."""

    name = "remove_non_numeric_trailing_dots"

    def __call__(self, text: str, operators: LanguageOperators) -> str:
        return re.sub(r"\.([^0-9]|$)", r" \1", text)
