import re

from normalization.constants.protectors import SEPARATE_NUMBER_TEMPLATE
from normalization.languages.base import LanguageOperators
from normalization.steps.base import TextStep
from normalization.steps.registry import register_step


@register_step
class FoldSpelledOrdinalsStep(TextStep):
    """Write spelled ordinals as the digits of their number (fr 'premier' -> '1').

    Reads ``operators.config.spelled_ordinals``: whole words, matched case-insensitively,
    longest first. Runs before expand_written_numbers_to_digits so a glued compound
    ('tjugoförsta') is read whole, not split into a cardinal and an ordinal.
    The digits sit between ¶ marks, so no digit-collapse pass glues them to a number
    next to them ('premier 93' -> '1 93', not '193'); restore_number_list_commas
    turns the marks into spaces.
    """

    name = "fold_spelled_ordinals"

    def __call__(self, text: str, operators: LanguageOperators) -> str:
        spelled = operators.config.spelled_ordinals
        if not spelled:
            return text
        by_word = {word.casefold(): digits for word, digits in spelled.items()}
        alternation = "|".join(
            re.escape(word)
            for word in sorted(by_word, key=lambda w: len(w), reverse=True)
        )
        pattern = re.compile(rf"(?<!\w)(?:{alternation})(?!\w)", re.IGNORECASE)
        return pattern.sub(
            lambda m: SEPARATE_NUMBER_TEMPLATE.format(by_word[m.group(0).casefold()]),
            text,
        )
