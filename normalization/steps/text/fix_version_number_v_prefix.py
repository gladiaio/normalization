import re

from normalization.languages.base import LanguageOperators
from normalization.steps.base import TextStep
from normalization.steps.registery import register_step


@register_step
class FixVersionNumberVPrefixStep(TextStep):
    """Collapse space between 'v' and digit (v 2 -> v2). 'v' must be followed by a digit."""

    name = "fix_version_number_v_prefix"

    def __call__(self, text: str, operators: LanguageOperators) -> str:
        return re.sub(r"\bv\s+(\d)", r"v\1", text)
