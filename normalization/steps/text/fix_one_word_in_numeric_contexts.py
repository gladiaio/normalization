from normalization.languages.base import LanguageOperators
from normalization.steps.base import TextStep
from normalization.steps.registry import register_step


@register_step
class FixOneWordInNumericContextsStep(TextStep):
    """Convert the word for 'one' to its digit when adjacent to other digits.

    Example (English): '10 one one' -> '10 1 1', 'one 5' -> '1 5'
    """

    name = "fix_one_word_in_numeric_contexts"

    def __call__(self, text: str, operators: LanguageOperators) -> str:
        return operators.fix_one_word_in_numeric_contexts(text)
