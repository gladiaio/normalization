import re

from normalization.languages.base import LanguageOperators
from normalization.steps.base import TextStep
from normalization.steps.registry import register_step


@register_step
class RemoveThousandSeparatorsStep(TextStep):
    """Remove thousand separators based on the language config.

    English uses comma (1,234 -> 1234), European languages use period (1.234 -> 1234).
    """

    name = "remove_thousand_separators"

    def __call__(self, text: str, operators: LanguageOperators) -> str:
        sep = re.escape(operators.config.thousand_separator)
        dec = re.escape(operators.config.decimal_separator)
        full = re.compile(rf"(\d){sep}(\d{{3}}(?:{sep}\d{{3}})*(?:{dec}\d+)?)\b")
        simple = re.compile(rf"(\d){sep}(\d{{3}})\b")
        text = full.sub(r"\1\2", text)
        text = simple.sub(r"\1\2", text)
        return text
