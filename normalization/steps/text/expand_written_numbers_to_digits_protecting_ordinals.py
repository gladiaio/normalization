from normalization.languages.base import LanguageOperators
from normalization.steps.base import TextStep
from normalization.steps.registry import register_step


@register_step
class ExpandWrittenNumbersToDigitsProtectingOrdinalsStep(TextStep):
    """Convert written numbers to digits, holding the ordinals it reads as placeholders.

    Same as expand_written_numbers_to_digits, except that an ordinal the expansion
    reads (da 'første', 'enogtyvende') becomes an ordinal placeholder, which
    restore_ordinals writes with the language's canonical suffix ('1.', '21.').
    Delegates to operators.expand_written_numbers_protecting_ordinals().
    """

    name = "expand_written_numbers_to_digits_protecting_ordinals"

    def __call__(self, text: str, operators: LanguageOperators) -> str:
        return operators.expand_written_numbers_protecting_ordinals(text)
