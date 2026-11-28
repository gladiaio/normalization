import re

from normalization.constants.protectors import SEPARATE_NUMBER_TEMPLATE
from normalization.languages.base import LanguageOperators
from normalization.steps.base import TextStep
from normalization.steps.registry import register_step


@register_step
class StripOrdinalSuffixesStep(TextStep):
    """Drop the suffix of a digit ordinal (fr '1er' -> '1', sv '1:a' -> '1', es '1º' -> '1').

    Only when ``operators.config.strip_ordinal_suffixes`` is True, with the suffixes of
    ``operators.config.ordinal_suffixes``. The token must be digits then a suffix, alone:
    a digit or letter before it ('AF1er') or a letter after it ('1e5') leaves it a code.
    Runs before expand_alphanumeric_codes, which would space the suffix out letter by
    letter, and before remove_diacritics, which turns 'º' into 'o'.
    The digits sit between ¶ marks, so no digit-collapse pass glues them to a number
    next to them ('1er 93' -> '1 93', not '193'); restore_number_list_commas turns the
    marks into spaces.
    """

    name = "strip_ordinal_suffixes"

    def __call__(self, text: str, operators: LanguageOperators) -> str:
        suffixes = operators.config.ordinal_suffixes
        if not operators.config.strip_ordinal_suffixes or not suffixes:
            return text
        alternation = "|".join(
            re.escape(suffix)
            for suffix in sorted(suffixes, key=lambda s: len(s), reverse=True)
        )
        pattern = re.compile(
            rf"(?<![\w.,])(\d+)(?:{alternation})(?![\w])", re.IGNORECASE
        )
        return pattern.sub(lambda m: SEPARATE_NUMBER_TEMPLATE.format(m.group(1)), text)
