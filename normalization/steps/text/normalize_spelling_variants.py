from normalization.languages.base import LanguageOperators
from normalization.steps.base import TextStep
from normalization.steps.registry import register_step


@register_step
class NormalizeSpellingVariantsStep(TextStep):
    """Fold context-dependent spelling variants of the same word. Delegates to operators.normalize_spelling_variants().

    Runs right after apply_character_replacements, so that every later step
    (numbers, symbols, word replacements) sees one spelling. No-op for a
    language that does not override the operator method.
    """

    name = "normalize_spelling_variants"

    def __call__(self, text: str, operators: LanguageOperators) -> str:
        return operators.normalize_spelling_variants(text)
