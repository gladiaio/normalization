import re

from normalization.languages.base import LanguageOperators
from normalization.steps.base import TextStep
from normalization.steps.registry import register_step


@register_step
class ApplySentenceLevelReplacementsStep(TextStep):
    """Apply multi-word phrase replacements (e.g. 'good bye' -> 'goodbye').

    Reads operators.config.sentence_replacements. Applies longest match first so that more specific phrases take priority over shorter overlapping ones.
    No effect when the dict is empty.
    """

    name = "apply_sentence_level_replacements"

    def __call__(self, text: str, operators: LanguageOperators) -> str:
        replacements = operators.config.sentence_replacements
        if replacements is None:
            # TODO: warn or log when sentence_replacements is not configured for this language
            return text
        for pattern, replacement in sorted(
            replacements.items(), key=lambda x: len(x[0]), reverse=True
        ):
            text = re.sub(
                rf"\b{re.escape(pattern)}\b", replacement, text, flags=re.IGNORECASE
            )
        return text
