from normalization.languages.base import LanguageOperators
from normalization.steps.base import TextStep
from normalization.steps.registery import register_step


@register_step
class CasefoldTextStep(TextStep):
    """Lowercase all text using str.casefold()."""

    name = "casefold_text"

    def __call__(self, text: str, operators: LanguageOperators) -> str:
        return text.casefold()
