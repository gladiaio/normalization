import re

from normalization.languages.base import LanguageOperators
from normalization.steps.base import TextStep
from normalization.steps.registry import register_step

_ROMAN_REPLACEMENTS: dict[str, str] = {
    "ii": "2",
    "iii": "3",
    "iv": "4",
    "v": "5",
    "vi": "6",
    "vii": "7",
    "viii": "8",
    "ix": "9",
}


@register_step
class ConvertRomanNumeralsToDigitsStep(TextStep):
    """Convert simple Roman numerals (II-IX) to Arabic digits in full text.

    Runs before expand_alphanumeric_codes to prevent 'VIII' -> 'V I I I'.
    Only converts ii-ix to avoid false positives with single letters like 'I'.
    Skips 'v' when adjacent to digits (version-like contexts: v2, v 12).
    """

    name = "convert_roman_numerals_to_digits"

    def __call__(self, text: str, operators: LanguageOperators) -> str:
        for roman, arabic in _ROMAN_REPLACEMENTS.items():
            if roman == "v":
                text = re.sub(
                    r"(?<!\d )(?<!\d)\bv\b(?!\s*\d)",
                    arabic,
                    text,
                    flags=re.IGNORECASE,
                )
            else:
                text = re.sub(rf"\b{roman}\b", arabic, text, flags=re.IGNORECASE)
        return text
