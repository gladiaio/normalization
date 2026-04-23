import re
import unicodedata

from normalization.constants.protectors import ProtectPlaceholder
from normalization.languages.base import LanguageOperators
from normalization.steps.base import TextStep
from normalization.steps.registry import register_step

_KEEP_CHARS = "".join(p.value for p in ProtectPlaceholder) + "€$£¥¢%"


@register_step
class RemoveSymbolsStep(TextStep):
    """Replace markers, symbols, and punctuation with spaces.

    Preserves letters, digits, and all placeholder characters. When
    ``symbols_to_words`` defines a word for ``%``, expands ``%`` only when it
    follows a decimal or integer literal (e.g. ``8,75%``), so other ``%`` uses
    stay unchanged.
    """

    name = "remove_symbols"

    def __call__(self, text: str, operators: LanguageOperators) -> str:
        text = unicodedata.normalize("NFKC", text)
        pct_word = operators.config.symbols_to_words.get("%")
        if pct_word:
            # Only expand ``%`` after numeric literals (e.g. 8,75%) so brand-style
            # strings like ``Signal%%Mark`` stay intact.
            text = re.sub(
                rf"(\d+(?:[.,]\d+)?)\s*{re.escape('%')}",
                rf"\1 {pct_word}",
                text,
            )
        return "".join(
            c if c in _KEEP_CHARS else " " if unicodedata.category(c)[0] in "MSP" else c
            for c in text
        )
