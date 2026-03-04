import re

from normalization.constants.protectors import ProtectPlaceholder
from normalization.languages.base import LanguageOperators
from normalization.steps.base import TextStep
from normalization.steps.registery import register_step

_RE_SPACES_BETWEEN_DIGITS = re.compile(r"(\d)\s+(?=\d+(?![a-z]))")


@register_step
class RemoveSpacesBetweenAdjacentDigitsStep(TextStep):
    """Collapse spaces between adjacent digits (1 2 3 -> 123).

    Preserves spaces around 'point' (decimal word) and before ordinals.
    Handles ¤ markers by processing segments separately.
    """

    name = "remove_spaces_between_adjacent_digits"

    def __call__(self, text: str, operators: LanguageOperators) -> str:
        decimal_word = operators.config.decimal_word
        sep = ProtectPlaceholder.NUMBER_SEPARATOR.value

        text = text.replace(f" {decimal_word} ", f"X{decimal_word.upper()}X")

        ordinals: list[str] = []
        ordinal_suffixes = operators.config.ordinal_suffixes

        if ordinal_suffixes:
            suffix_alt = "|".join(re.escape(s) for s in ordinal_suffixes)
            ordinal_re = re.compile(rf"(\s)(\d+)({suffix_alt})\b")

            def _protect_ordinal(match: re.Match) -> str:
                ordinals.append(match.group(0))
                return f" XORDINAL{len(ordinals) - 1}X"

            text = ordinal_re.sub(_protect_ordinal, text)

        if sep not in text:
            text = _RE_SPACES_BETWEEN_DIGITS.sub(r"\1", text)
        else:
            parts = text.split(sep)
            parts = [_RE_SPACES_BETWEEN_DIGITS.sub(r"\1", p) for p in parts]
            text = sep.join(parts)

        for i, ordinal in enumerate(ordinals):
            text = text.replace(f"XORDINAL{i}X", ordinal.strip())

        text = text.replace(f"X{decimal_word.upper()}X", f" {decimal_word} ")

        return text
