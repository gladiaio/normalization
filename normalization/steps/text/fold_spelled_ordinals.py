import re

from normalization.constants.protectors import ordinal_placeholder
from normalization.languages.base import LanguageOperators
from normalization.steps.base import TextStep
from normalization.steps.registry import register_step


@register_step
class FoldSpelledOrdinalsStep(TextStep):
    """Hold spelled ordinals as ordinal placeholders (fr 'premier' -> the ordinal 1).

    Reads ``operators.config.spelled_ordinals``: whole words, matched case-insensitively,
    longest first, so a glued compound ('tjugoförsta') is read whole. Runs after
    expand_written_numbers_to_digits, so a compound the expansion reads
    ('vingt-deuxième' -> '22ème') is not split into a cardinal and an ordinal.
    restore_ordinals writes the placeholder as digits plus the language's canonical
    suffix ('1er'), the same form a digit ordinal ('1re') gets.
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
            lambda m: ordinal_placeholder(by_word[m.group(0).casefold()]), text
        )
