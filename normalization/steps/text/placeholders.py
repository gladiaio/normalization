"""All protect/restore placeholder step pairs.

Every protect step in Stage 1 has a matching restore step in Stage 3.
They live together in this file to keep the dependency explicit.
"""

import re

from normalization.constants.protectors import ProtectPlaceholder
from normalization.languages.base import LanguageOperators
from normalization.steps.base import ProtectStep, RestoreStep, TextStep
from normalization.steps.registry import register_step

# ---------------------------------------------------------------------------
# Email symbols
# ---------------------------------------------------------------------------

_RE_EMAIL = re.compile(r"[a-zA-Z0-9_.+\-]+@[a-zA-Z0-9\-]+\.[a-zA-Z0-9.\-]+")


@register_step
class ProtectEmailSymbolsStep(TextStep):
    """Replace @ and . inside email addresses with placeholders.

    A single email match requires protecting two different symbols (@ → EMAIL_AT, . → EMAIL_DOT) in one pass. ProtectStep handles exactly one placeholder per substitution.
    """

    name = "protect_email_symbols"

    def __call__(self, text: str, operators: LanguageOperators) -> str:
        def _replace_email(match: re.Match) -> str:
            email = match.group(0)
            email = email.replace("@", f" {ProtectPlaceholder.EMAIL_AT.value} ")
            email = email.replace(".", f" {ProtectPlaceholder.EMAIL_DOT.value} ")
            return email

        return _RE_EMAIL.sub(_replace_email, text)


@register_step
class RestoreEmailAtSymbolWithWordStep(TextStep):
    """Restore XATX placeholder with the language-specific 'at' word.

    When no word is configured for '@', restores the original '@' character
    so that placeholders never leak into the final output.
    """

    name = "restore_email_at_symbol_with_word"

    def __call__(self, text: str, operators: LanguageOperators) -> str:
        at_word = operators.config.symbols_to_words.get("@")
        if at_word is None:
            return text
        text = re.sub(
            rf"\s*{re.escape(ProtectPlaceholder.EMAIL_AT.value)}\s*",
            f" {at_word} ",
            text,
            flags=re.IGNORECASE,
        )
        return text


@register_step
class RestoreEmailDotSymbolWithWordStep(TextStep):
    """Restore XDOTX placeholder with the language-specific 'dot' word.

    When no word is configured for '.', restores the original '.' character
    so that placeholders never leak into the final output.
    """

    name = "restore_email_dot_symbol_with_word"

    def __call__(self, text: str, operators: LanguageOperators) -> str:
        dot_word = operators.config.symbols_to_words.get(".")
        if dot_word is None:
            return text
        text = re.sub(
            rf"\s*{re.escape(ProtectPlaceholder.EMAIL_DOT.value)}\s*",
            f" {dot_word} ",
            text,
            flags=re.IGNORECASE,
        )
        return text


# ---------------------------------------------------------------------------
# Phone plus symbol
# ---------------------------------------------------------------------------

_RE_PLUS_DIGIT = re.compile(r"\+(?=\d)")
_RE_PLUS_SPACE_DIGIT = re.compile(r"\+\s+(\d)")


@register_step
class ProtectPhonePlusSymbolStep(TextStep):
    """Replace "+" when it appears right before a digit (like in phone numbers) with a special placeholder.

    The regex pattern "\\+(?=\\d)" means:
    - Match a literal "+" character
    - But only if it is immediately followed by a number (0-9)
    - The digit is NOT included in the match (it stays untouched)

    For example:
    "+123456" → the "+" is replaced, but "123456" stays the same.

    Note: The pattern uses a lookahead (?=\\d), which checks what comes next
    without capturing it as part of the match.
    """

    name = "protect_phone_plus_symbol"

    def __call__(self, text: str, operators: LanguageOperators) -> str:
        return _RE_PLUS_DIGIT.sub(ProtectPlaceholder.PHONE_PLUS.value, text)


@register_step
class RestorePhonePlusSymbolStep(TextStep):
    """Restore XPLUSX placeholder back to + and collapse trailing space.

    Beyond the plain replace, it must also collapse "+ <digit>" → "+<digit>" (e.g. after casefold splits the token). RestoreStep only does plain string replacement.
    """

    name = "restore_phone_plus_symbol"

    def __call__(self, text: str, operators: LanguageOperators) -> str:
        text = text.replace(ProtectPlaceholder.PHONE_PLUS.value.lower(), "+")
        text = text.replace(ProtectPlaceholder.PHONE_PLUS.value, "+")
        text = _RE_PLUS_SPACE_DIGIT.sub(r"+\1", text)
        return text


# ---------------------------------------------------------------------------
# Time colon
# ---------------------------------------------------------------------------

_RE_TIME_COLON = re.compile(r"(\d{1,2}):(\d{2})")


@register_step
class ProtectTimeColonStep(ProtectStep):
    """Protect the colon used in time expressions like HH:MM.
    Matches times written with one or two digits for the hour and exactly two digits for the minutes (e.g., "9:30", "12:05").
    The colon between them is temporarily replaced with a placeholder so it is not modified or removed by later text-processing steps.

    Example:
    "9:30" → "9§30"  (colon replaced with placeholder)
    """

    name = "protect_time_colon"
    placeholder = ProtectPlaceholder.TIME_COLON

    def _pattern(self, operators: LanguageOperators) -> re.Pattern:
        return _RE_TIME_COLON


@register_step
class RestoreTimeColonStep(RestoreStep):
    """Restore § placeholder back to colon."""

    name = "restore_time_colon"
    placeholder = ProtectPlaceholder.TIME_COLON

    def _replacement(self, operators: LanguageOperators) -> str:
        return ":"


# ---------------------------------------------------------------------------
# Unit decimal  (9.8 m/s -> 9‡8 m/s)
# ---------------------------------------------------------------------------

_RE_DECIMAL_IN_UNIT = re.compile(r"(\d+)\.(\d+)(?=\s*(?:km|m)/[hs]\b)")


@register_step
class ProtectUnitDecimalStep(ProtectStep):
    """Replace . in decimal unit expressions with ‡ placeholder (e.g. 9.8 m/s → 9‡8 m/s)."""

    name = "protect_unit_decimal"
    placeholder = ProtectPlaceholder.UNIT_DECIMAL

    def _pattern(self, operators: LanguageOperators) -> re.Pattern:
        return _RE_DECIMAL_IN_UNIT


# ---------------------------------------------------------------------------
# Unit slash  (km/h, m/s -> km†h, m†s)
# ---------------------------------------------------------------------------

_RE_UNIT_SLASH = re.compile(r"\b(km|m)/([hs])\b")


@register_step
class ProtectUnitSlashStep(ProtectStep):
    """Replace / in unit expressions with † placeholder (e.g. km/h → km†h)."""

    name = "protect_unit_slash"
    placeholder = ProtectPlaceholder.UNIT_SLASH

    def _pattern(self, operators: LanguageOperators) -> re.Pattern:
        return _RE_UNIT_SLASH


@register_step
class RestoreUnitSlashStep(RestoreStep):
    """Restore † placeholder back to /."""

    name = "restore_unit_slash"
    placeholder = ProtectPlaceholder.UNIT_SLASH

    def _replacement(self, operators: LanguageOperators) -> str:
        return "/"


@register_step
class RestoreUnitDecimalAsWordStep(RestoreStep):
    """Restore ‡ placeholder with the language-specific decimal word."""

    name = "restore_unit_decimal_as_word"
    placeholder = ProtectPlaceholder.UNIT_DECIMAL

    def _replacement(self, operators: LanguageOperators) -> str:
        if operators.config.decimal_word is None:
            return " "
        return f" {operators.config.decimal_word} "


# ---------------------------------------------------------------------------
# Number separator commas  (1, 2, 3 -> 1 ¤ 2 ¤ 3)
# ---------------------------------------------------------------------------

_RE_COMMA_SEP = re.compile(r"(\d+),\s+(?=\d)")
_RE_DOT_SEP = re.compile(r"(\d+)\.\s+(?=\d)")


@register_step
class ProtectNumberSeparatorCommasStep(TextStep):
    """Replace comma/dot+space between digits with ¤ marker. (1, 2, 3 -> 1 ¤ 2 ¤ 3)

    Two independent patterns (comma-separated and
    dot-separated) both collapse to the same marker. ProtectStep handles a
    single pattern mapping to a single placeholder.
    """

    name = "protect_number_separator_commas"

    def __call__(self, text: str, operators: LanguageOperators) -> str:
        text = _RE_COMMA_SEP.sub(
            rf"\1 {ProtectPlaceholder.NUMBER_SEPARATOR.value} ",
            text,
        )
        text = _RE_DOT_SEP.sub(
            rf"\1 {ProtectPlaceholder.NUMBER_SEPARATOR.value} ",
            text,
        )
        return text


@register_step
class RemoveNumberSeparatorMarkersStep(TextStep):
    """Strip ¤ markers from the text.

    Uses TextStep directly: the marker is deleted entirely (not restored to a
    character or word). RestoreStep replaces with a non-empty string; here the
    surrounding whitespace must also be collapsed to nothing.
    """

    name = "remove_number_separator_markers"

    def __call__(self, text: str, operators: LanguageOperators) -> str:
        return re.sub(
            rf"\s*{re.escape(ProtectPlaceholder.NUMBER_SEPARATOR.value)}\s*",
            "",
            text,
        )


# ---------------------------------------------------------------------------
# Decimal separator  (moved from protect_decimal_separator.py)
# ---------------------------------------------------------------------------


@register_step
class ProtectDecimalSeparatorStep(ProtectStep):
    """Protect the decimal separator from being removed by RemoveSymbolsStep."""

    name = "protect_decimal_separator"
    placeholder = ProtectPlaceholder.DECIMAL_SEPARATOR

    def _pattern(self, operators: LanguageOperators) -> re.Pattern:
        safe_separator = re.escape(operators.config.decimal_separator)
        return re.compile(rf"(\d+){safe_separator}(\d+)")


@register_step
class RestoreDecimalSeparatorWithWordStep(RestoreStep):
    """Restore XDECIMALX placeholder with the language-specific decimal word."""

    name = "restore_decimal_separator_with_word"
    placeholder = ProtectPlaceholder.DECIMAL_SEPARATOR

    def _replacement(self, operators: LanguageOperators) -> str:
        if operators.config.decimal_word is None:
            return " "
        return f" {operators.config.decimal_word} "


# ---------------------------------------------------------------------------
# Hyphenated letter spelling  (b-o-b -> bxltrx oxltrx bxltrx)
# ---------------------------------------------------------------------------


@register_step
class ProtectHyphenatedLetterSpellingStep(TextStep):
    """Mark single-letter-hyphen sequences to prevent false conversions.

    Uses TextStep directly: the replacement is a per-match function that splits on '-' and suffixes each individual letter. Example: "b-o-b" → "bxltrx oxltrx bxltrx".
    """

    name = "protect_hyphenated_letter_spelling"

    def __call__(self, text: str, operators: LanguageOperators) -> str:
        def _add_marker(match: re.Match) -> str:
            letters = match.group(0).split("-")
            suffix = ProtectPlaceholder.SPELLING_SUFFIX.value
            return " ".join(f"{letter}{suffix}" for letter in letters)

        return re.sub(r"\b([a-zA-Z](?:-[a-zA-Z])+)\b", _add_marker, text)


# ---------------------------------------------------------------------------
# Space-separated letter spelling  (j o h a n n -> jxltrx oxltrx ...)
# ---------------------------------------------------------------------------


@register_step
class ProtectSpaceSeparatedLetterSpellingStep(TextStep):
    """Mark sequences of 3+ single letters to prevent false conversions.

    Uses TextStep directly: same reason as ProtectHyphenatedLetterSpellingStep —
    the replacement is a per-match function that suffixes each individual letter.
    """

    name = "protect_space_separated_letter_spelling"

    def __call__(self, text: str, operators: LanguageOperators) -> str:
        def _add_marker(match: re.Match) -> str:
            letters = match.group(0).split()
            suffix = ProtectPlaceholder.SPELLING_SUFFIX.value
            return " ".join(f"{letter}{suffix}" for letter in letters)

        return re.sub(r"\b([a-zA-Z](?:\s+[a-zA-Z]){2,})\b", _add_marker, text)


@register_step
class RemoveLetterSpellingMarkersStep(TextStep):
    """Strip xltrx suffix markers from letters.

    Uses TextStep directly: the suffix is a token-embedded string (not a
    standalone token), so removal requires a regex word-boundary match.
    Example: "bxltrx oxltrx bxltrx" → "b o b"
    """

    name = "remove_letter_spelling_markers"

    def __call__(self, text: str, operators: LanguageOperators) -> str:
        suffix = ProtectPlaceholder.SPELLING_SUFFIX.value
        return re.sub(rf"\b([a-z]){re.escape(suffix)}\b", r"\1", text)
