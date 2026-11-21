from normalization.languages.base import LanguageOperators
from normalization.languages.base.diacritics import remove_diacritics
from normalization.steps.base import TextStep
from normalization.steps.registry import register_step


@register_step
class RemoveDiacriticsStep(TextStep):
    """Normalize text by removing diacritics and converting special accented letters to their ASCII equivalents. (é -> e, ê -> e, etc.)"""

    name = "remove_diacritics"

    def __call__(self, text: str, operators: LanguageOperators) -> str:
        return remove_diacritics(text)
