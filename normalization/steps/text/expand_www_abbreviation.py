import re

from normalization.languages.base import LanguageOperators
from normalization.steps.base import TextStep
from normalization.steps.registery import register_step


@register_step
class ExpandWwwAbbreviationStep(TextStep):
    """Expand 'www' to 'W W W'."""

    name = "expand_www_abbreviation"

    def __call__(self, text: str, operators: LanguageOperators) -> str:
        return re.sub(r"\bwww\b", "W W W", text, flags=re.IGNORECASE)
