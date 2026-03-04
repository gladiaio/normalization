import re

from normalization.languages.base import LanguageOperators
from normalization.steps.base import TextStep
from normalization.steps.registery import register_step


@register_step
class RemoveFillerWordsStep(TextStep):
    """Remove filler words defined in the language config (um, uh, euh, etc.)."""

    name = "remove_filler_words"

    def __call__(self, text: str, operators: LanguageOperators) -> str:
        fillers = operators.config.filler_words
        if not fillers:
            return text
        pattern = r"\b(?:" + "|".join(re.escape(f) for f in fillers) + r")\b[,.]?\s*"
        return re.sub(pattern, "", text, flags=re.IGNORECASE)
