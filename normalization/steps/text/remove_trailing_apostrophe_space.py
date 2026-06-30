import re

from normalization.languages.base import LanguageOperators
from normalization.steps.base import TextStep
from normalization.steps.registry import register_step

# Orphan "s" left after remove_symbols turns "Latvia's" into "latvia s".
# Exclude literal letter/model references such as "the letter s" or "model s".
_RE_ORPHAN_POSSESSIVE_S = re.compile(
    r"\b(?!letter s\b)(?!model s\b)([a-z]{3,}) s\b",
    re.IGNORECASE,
)
_RE_WORD_POSSESSIVE_S = re.compile(r"\b(\w+)'s\b", re.IGNORECASE)


@register_step
class RemoveTrailingApostropheSpaceStep(TextStep):
    """Normalize apostrophe possessives before symbol stripping.

    Runs before remove_symbols so ``'s`` markers are removed while the apostrophe
    is still present. Also collapses orphan ``s`` tokens produced when symbol
    removal splits a possessive (``latvia s``), but not literal ``letter s`` or
    product names like ``model s``.
    """

    name = "remove_trailing_apostrophe_space"

    def __call__(self, text: str, operators: LanguageOperators) -> str:
        text = re.sub(r"\s+'", "'", text)
        text = _RE_WORD_POSSESSIVE_S.sub(r"\1", text)
        return _RE_ORPHAN_POSSESSIVE_S.sub(r"\1", text)
