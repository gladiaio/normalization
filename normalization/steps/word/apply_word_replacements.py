import re

from normalization.languages.base import LanguageOperators
from normalization.pipeline.replacer import Replacer
from normalization.steps.base import WordStep
from normalization.steps.registry import register_step

_RE_EMAIL = re.compile(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$")

_REPLACER_CACHE: dict[str, Replacer] = {}


def _get_replacer(operators: LanguageOperators) -> Replacer:
    code = operators.config.code
    if code not in _REPLACER_CACHE:
        _REPLACER_CACHE[code] = Replacer(operators.get_word_replacements())
    return _REPLACER_CACHE[code]


@register_step
class ApplyWordReplacementsStep(WordStep):
    """Apply single-word replacements from the language operators.

    Skips email tokens. Uses a cached Replacer keyed on the language code.
    """

    name = "apply_word_replacements"

    def __call__(self, word: str, operators: LanguageOperators) -> str:
        if _RE_EMAIL.match(word):
            return word
        replacer = _get_replacer(operators)
        return replacer(word).strip()
