import re

from normalization.languages.base import LanguageOperators
from normalization.steps.base import TextStep
from normalization.steps.registery import register_step


@register_step
class FormatTimePatternsWithAmpmStep(TextStep):
    """Format '5 45 p m' -> '5:45 pm' and '545 pm' -> '5:45 pm'.

    Reads operators.config.am_word and operators.config.pm_word.
    No-op when either is None.
    """

    name = "format_time_patterns_with_ampm"

    def __call__(self, text: str, operators: LanguageOperators) -> str:
        am_word = operators.config.am_word
        pm_word = operators.config.pm_word
        if am_word is None or pm_word is None:
            return text

        prefix_class = f"[{re.escape(am_word[0])}{re.escape(pm_word[0])}]"

        def _format_time(match: re.Match) -> str:
            hour = str(int(match.group(1)))
            minute = match.group(2)
            ampm = match.group(3)
            return f"{hour}:{minute} {ampm}m"

        def _format_compact_time(match: re.Match) -> str:
            digits = match.group(1)
            ampm = match.group(2)
            if len(digits) == 3:
                hour = str(int(digits[0]))
                minute = digits[1:3]
            else:
                hour = str(int(digits[0:2]))
                minute = digits[2:4]
            return f"{hour}:{minute} {ampm}m"

        text = re.sub(
            rf"\b(\d{{1,2}})\s+(\d{{2}})\s+({prefix_class})\s*m\b",
            _format_time,
            text,
        )
        text = re.sub(
            rf"\b(\d{{3,4}})\s+({prefix_class})\s*m\b",
            _format_compact_time,
            text,
        )
        return text
