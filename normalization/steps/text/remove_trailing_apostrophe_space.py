import re

from normalization.languages.base import LanguageOperators
from normalization.steps.base import TextStep
from normalization.steps.registry import register_step


@register_step
class RemoveTrailingApostropheSpaceStep(TextStep):
    """Remove space before apostrophe (' s -> 's) and orphan possessive s tokens.

    After remove_symbols, possessives like "Latvia's" become "latvia s"; collapse
    those back to the base word.
    """

    name = "remove_trailing_apostrophe_space"

    def __call__(self, text: str, operators: LanguageOperators) -> str:
        text = re.sub(r"\s+'", "'", text)
        return re.sub(r"\b([a-z]{2,}) s\b", r"\1", text)
