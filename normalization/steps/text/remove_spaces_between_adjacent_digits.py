import re

from normalization.constants.protectors import ProtectPlaceholder
from normalization.languages.base import LanguageOperators
from normalization.steps.base import TextStep
from normalization.steps.registry import register_step

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
        boundaries = (
            ProtectPlaceholder.NUMBER_SEPARATOR.value,
            ProtectPlaceholder.NUMBER_LIST_COMMA.value,
        )

        if decimal_word is not None:
            text = text.replace(f" {decimal_word} ", "XDECWORDX")

        ordinals: list[str] = []
        ordinal_suffixes = operators.config.ordinal_suffixes

        if ordinal_suffixes:
            suffix_alt = "|".join(re.escape(s) for s in ordinal_suffixes)
            ordinal_re = re.compile(rf"(\s)(\d+)({suffix_alt})\b")

            def _protect_ordinal(match: re.Match) -> str:
                ordinals.append(match.group(0))
                return f" XORDINAL{len(ordinals) - 1}X"

            text = ordinal_re.sub(_protect_ordinal, text)

        present = [b for b in boundaries if b in text]
        if not present:
            text = _RE_SPACES_BETWEEN_DIGITS.sub(r"\1", text)
        else:
            # Split on every boundary marker so collapse cannot cross list commas
            # ("60 ¶ 70") or joinable separators ("1 ¤ 2").
            pattern = "|".join(re.escape(b) for b in present)
            bits = re.split(f"({pattern})", text)
            text = "".join(
                bit if bit in present else _RE_SPACES_BETWEEN_DIGITS.sub(r"\1", bit)
                for bit in bits
            )

        for i, ordinal in enumerate(ordinals):
            text = text.replace(f"XORDINAL{i}X", ordinal.strip())

        if decimal_word is not None:
            text = text.replace("XDECWORDX", f" {decimal_word} ")

        return text
