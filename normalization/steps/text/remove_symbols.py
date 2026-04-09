import unicodedata

from normalization.constants.protectors import ProtectPlaceholder
from normalization.languages.base import LanguageOperators
from normalization.steps.base import TextStep
from normalization.steps.registry import register_step

_KEEP_CHARS = "".join(p.value for p in ProtectPlaceholder) + "€$£¥¢%"


@register_step
class RemoveSymbolsStep(TextStep):
    """Replace markers, symbols, and punctuation with spaces.

    Preserves letters, digits, and all placeholder characters.
    """

    name = "remove_symbols"

    def __call__(self, text: str, operators: LanguageOperators) -> str:
        return "".join(
            c if c in _KEEP_CHARS else " " if unicodedata.category(c)[0] in "MSP" else c
            for c in unicodedata.normalize("NFKC", text)
        )
