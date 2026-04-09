from normalization.languages.base import LanguageOperators
from normalization.steps.base import TextStep
from normalization.steps.registry import register_step


@register_step
class ExpandWrittenNumbersToDigitsStep(TextStep):
    """Convert written numbers to digits (fifty -> 50, twenty three -> 23). Delegates to operators.expand_written_numbers()."""

    name = "expand_written_numbers_to_digits"

    def __call__(self, text: str, operators: LanguageOperators) -> str:
        return operators.expand_written_numbers(text)
