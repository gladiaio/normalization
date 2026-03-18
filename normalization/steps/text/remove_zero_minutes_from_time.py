import re

from normalization.languages.base import LanguageOperators
from normalization.steps.base import TextStep
from normalization.steps.registry import register_step


@register_step
class RemoveZeroMinutesFromTimeStep(TextStep):
    """Remove :00 from time expressions (10:00 pm -> 10 pm).

    Reads operators.config.am_word and operators.config.pm_word.
    No-op when either is None.
    """

    name = "remove_zero_minutes_from_time"

    def __call__(self, text: str, operators: LanguageOperators) -> str:
        am_word = operators.config.am_word
        pm_word = operators.config.pm_word
        if am_word is None or pm_word is None:
            return text

        ampm_alt = f"({re.escape(am_word)}|{re.escape(pm_word)})"
        return re.sub(
            rf"\b(\d{{1,2}}):00\s+{ampm_alt}\b",
            r"\1 \2",
            text,
            flags=re.IGNORECASE,
        )
