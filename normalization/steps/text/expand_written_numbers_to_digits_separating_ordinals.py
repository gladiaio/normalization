from normalization.languages.base import LanguageOperators
from normalization.steps.base import TextStep
from normalization.steps.registry import register_step


@register_step
class ExpandWrittenNumbersToDigitsSeparatingOrdinalsStep(TextStep):
    """Convert written numbers to digits, keeping an ordinal apart from the next number.

    Same as expand_written_numbers_to_digits, except that an ordinal the expansion
    writes sits between ¶ marks (da 'første 2 maj' -> '1 2 maj', not '12 maj').
    Delegates to operators.expand_written_numbers_separating_ordinals();
    restore_number_list_commas turns the marks into spaces.
    """

    name = "expand_written_numbers_to_digits_separating_ordinals"

    def __call__(self, text: str, operators: LanguageOperators) -> str:
        return operators.expand_written_numbers_separating_ordinals(text)
