import re

from normalization.languages.base import LanguageOperators
from normalization.steps.base import TextStep
from normalization.steps.registery import register_step


@register_step
class RemoveTrailingApostropheSpaceStep(TextStep):
    """Remove space before apostrophe (' s -> 's)."""

    name = "remove_trailing_apostrophe_space"

    def __call__(self, text: str, operators: LanguageOperators) -> str:
        return re.sub(r"\s+'", "'", text)
