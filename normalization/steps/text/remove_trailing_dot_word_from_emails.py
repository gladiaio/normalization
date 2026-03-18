import re

from normalization.languages.base import LanguageOperators
from normalization.steps.base import TextStep
from normalization.steps.registry import register_step


@register_step
class RemoveTrailingDotWordFromEmailsStep(TextStep):
    """Remove trailing 'dot' after email-like words at end of text."""

    name = "remove_trailing_dot_word_from_emails"

    def __call__(self, text: str, operators: LanguageOperators) -> str:
        dot_word = operators.config.symbols_to_words.get(".")
        if dot_word is None:
            return text
        return re.sub(
            rf"([a-z]{{2,}})\s+{re.escape(dot_word)}\s*$",
            r"\1",
            text,
        )
