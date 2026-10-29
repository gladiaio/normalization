from normalization.languages.base import LanguageOperators
from normalization.steps.base import TextStep
from normalization.steps.registry import register_step


@register_step
class ApplyCharacterReplacementsStep(TextStep):
    """Replace or delete single characters using ``character_replacements`` from the language config.

    Runs first in the pipeline so that script-level variants (letter forms, native
    digits, vowel marks) are unified before protection, numeric, and symbol steps.
    Skipped when the language does not define ``character_replacements``.
    """

    name = "apply_character_replacements"

    def __call__(self, text: str, operators: LanguageOperators) -> str:
        replacements = operators.config.character_replacements
        # TODO: populate character_replacements for languages with script-level variants
        if replacements is None:
            return text
        return text.translate(str.maketrans(replacements))
