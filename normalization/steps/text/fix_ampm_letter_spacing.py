import re

from normalization.languages.base import LanguageOperators
from normalization.steps.base import TextStep
from normalization.steps.registry import register_step


@register_step
class FixAmpmLetterSpacingStep(TextStep):
    """Collapse 'a m' / 'p m' into 'am' / 'pm' after time digits.

    Reads operators.config.am_word and operators.config.pm_word.
    No-op when either is None.
    """

    name = "fix_ampm_letter_spacing"

    def __call__(self, text: str, operators: LanguageOperators) -> str:
        am_word = operators.config.am_word
        pm_word = operators.config.pm_word
        if am_word is None or pm_word is None:
            return text

        prefix_class = f"[{re.escape(am_word[0])}{re.escape(pm_word[0])}]"
        return re.sub(rf"\b(\d+:?\d*\s+)({prefix_class})\s+m\b", r"\1\2m", text)
