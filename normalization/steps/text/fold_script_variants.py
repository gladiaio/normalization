from normalization.languages.base import LanguageOperators
from normalization.steps.base import TextStep
from normalization.steps.registry import register_step


@register_step
class FoldScriptVariantsStep(TextStep):
    """Fold spellings of one word that differ only by script or writing convention.

    Delegates to ``operators.fold_script_variants``; a no-op for every language
    that does not override it. Japanese folds katakana to hiragana, expands the
    iteration mark 々, drops a word-final ー and unifies the counter ヶ/ヵ/か.
    Runs first, on the composed text, before any mark or symbol removal.
    """

    name = "fold_script_variants"

    def __call__(self, text: str, operators: LanguageOperators) -> str:
        return operators.fold_script_variants(text)
