import re
import unicodedata

from normalization.constants.protectors import ProtectPlaceholder
from normalization.languages.base import LanguageOperators
from normalization.steps.base import TextStep
from normalization.steps.registry import register_step

_KEEP_CHARS = "".join(p.value for p in ProtectPlaceholder) + "€$£¥¢%"

# A geresh or gershayim inside a Hebrew word (an abbreviation such as "צה\"ל", or a loan sound
# such as "ג'"), written with the Hebrew signs or the ASCII quotes: part of the word, not a break.
_HEBREW_WORD_QUOTE = re.compile(
    r"(?<=[\u05d0-\u05ea])[\"'\u05f3\u05f4](?=[\u05d0-\u05ea])"
)


@register_step
class RemoveSymbolsStep(TextStep):
    """Replace symbols and punctuation with spaces.

    Preserves letters, digits, combining marks (removed or kept with their
    letter by ``remove_diacritics``) and all placeholder characters. A geresh
    or gershayim between two Hebrew letters is removed, which keeps the word
    whole (``צה"ל`` -> ``צהל``). When
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
        text = _HEBREW_WORD_QUOTE.sub("", text)
        return "".join(
            c if c in _KEEP_CHARS else " " if unicodedata.category(c)[0] in "SP" else c
            for c in text
        )
