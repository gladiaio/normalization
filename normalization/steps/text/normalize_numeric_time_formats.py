from normalization.languages.base import LanguageOperators
from normalization.steps.base import TextStep
from normalization.steps.registry import register_step


@register_step
class NormalizeNumericTimeFormatsStep(TextStep):
    """Normalize numeric time formats (05:45pm -> 5:45 pm, 5.45 p.m. -> 5:45 pm).

    Delegates to operators.normalize_numeric_time_formats().
    """

    name = "normalize_numeric_time_formats"

    def __call__(self, text: str, operators: LanguageOperators) -> str:
        return operators.normalize_numeric_time_formats(text)
