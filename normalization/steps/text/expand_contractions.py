from normalization.languages.base import LanguageOperators
from normalization.steps.base import TextStep
from normalization.steps.registry import register_step


@register_step
class ExpandContractionsStep(TextStep):
    """Expand contractions (it's -> it is, can't -> cannot).

    Delegates to operators.expand_contractions().
    """

    name = "expand_contractions"

    def __call__(self, text: str, operators: LanguageOperators) -> str:
        return operators.expand_contractions(text)
