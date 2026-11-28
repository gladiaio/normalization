"""All protect/restore placeholder step pairs.

Every protect step in Stage 1 has a matching restore step in Stage 3.
They live together in this file to keep the dependency explicit.
"""

import re

from normalization.constants.protectors import (
    ORDINAL_DIGIT_LETTERS,
    ORDINAL_PLACEHOLDER_END,
    ORDINAL_PLACEHOLDER_PREFIX,
    ProtectPlaceholder,
    ordinal_placeholder,
    ordinal_placeholder_digits,
)
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

# Multi-digit list commas first ("60, 70") so they are not treated as joinable
# digit-sequence separators.
_RE_MULTI_DIGIT_LIST_COMMA = re.compile(r"(\d{2,}),\s+(?=\d{2,})")
_RE_COMMA_SEP = re.compile(r"(\d+),\s+(?=\d)")
_RE_DOT_SEP = re.compile(r"(\d+)\.\s+(?=\d)")


@register_step
class ProtectNumberSeparatorCommasStep(TextStep):
    """Protect commas/dots between digits before remove_symbols.

    - Multi-digit list commas ("60, 70") -> ¶ (restored as space after digit
      collapsing, so the groups stay separate).
    - Single-digit / mixed lists ("1, 2, 3") and spaced dots -> ¤ (stripped so
      the groups join).
    """

    name = "protect_number_separator_commas"

    def __call__(self, text: str, operators: LanguageOperators) -> str:
        list_sep = ProtectPlaceholder.NUMBER_LIST_COMMA.value
        join_sep = ProtectPlaceholder.NUMBER_SEPARATOR.value
        text = _RE_MULTI_DIGIT_LIST_COMMA.sub(rf"\1 {list_sep} ", text)
        text = _RE_COMMA_SEP.sub(rf"\1 {join_sep} ", text)
        text = _RE_DOT_SEP.sub(rf"\1 {join_sep} ", text)
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


@register_step
class RestoreNumberListCommasStep(TextStep):
    """Restore ¶ list-comma markers as a single space after digit collapsing."""

    name = "restore_number_list_commas"

    def __call__(self, text: str, operators: LanguageOperators) -> str:
        return re.sub(
            rf"\s*{re.escape(ProtectPlaceholder.NUMBER_LIST_COMMA.value)}\s*",
            " ",
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


# ---------------------------------------------------------------------------
# Ordinals  (1er -> xordxbx -> 1er; 2ème -> xordxcx -> 2e)
# ---------------------------------------------------------------------------


_RE_ORDINAL_PLACEHOLDER = re.compile(
    rf"{ORDINAL_PLACEHOLDER_PREFIX}([{ORDINAL_DIGIT_LETTERS}]+){ORDINAL_PLACEHOLDER_END}"
)


@register_step
class ProtectDigitOrdinalsStep(TextStep):
    """Hold digit ordinals as ordinal placeholders (fr '2ème' -> the ordinal 2).

    Uses TextStep directly: the placeholder carries the ordinal's number, spelled in
    letters, so it is built per match. Reads ``operators.config.digit_ordinal_suffixes``.
    The token must be digits then a suffix, alone: a digit or letter before it ('AF1er')
    or a letter after it ('1e5') leaves it a code. A suffix with no letter ('.') only
    counts before another word: '3. maj' is an ordinal, a sentence-final '3.' is not.
    Runs before expand_alphanumeric_codes, which would space the suffix out letter by
    letter, and before remove_diacritics, which turns 'º' into 'o'. restore_ordinals
    writes the placeholder back with the language's canonical suffix.
    """

    name = "protect_digit_ordinals"

    def __call__(self, text: str, operators: LanguageOperators) -> str:
        suffixes = operators.config.digit_ordinal_suffixes
        if not suffixes:
            return text
        alternatives = []
        for suffix in sorted(suffixes, key=lambda s: len(s), reverse=True):
            if any(c.isalpha() for c in suffix):
                alternatives.append(rf"{re.escape(suffix)}(?!\w)")
            else:
                alternatives.append(rf"{re.escape(suffix)}(?=\s+\w)")
        pattern = re.compile(
            rf"(?<![\w.,])(\d+)(?:{'|'.join(alternatives)})", re.IGNORECASE
        )
        return pattern.sub(lambda m: ordinal_placeholder(m.group(1)), text)


@register_step
class RestoreOrdinalsStep(TextStep):
    """Write each ordinal placeholder as digits plus the language's canonical suffix.

    Uses TextStep directly: the digits come from the placeholder and the suffix from
    ``operators.config.canonical_ordinal_suffix``, ``canonical_ordinal_suffix_by_number``
    and ``canonical_ordinal_suffix_by_ending`` (fr 'xordxbx' -> '1er', 'xordxcx' -> '2e').
    Runs last, so no later step can space out, strip or glue the suffix.
    """

    name = "restore_ordinals"

    def __call__(self, text: str, operators: LanguageOperators) -> str:
        if ORDINAL_PLACEHOLDER_PREFIX not in text:
            return text
        default = operators.config.canonical_ordinal_suffix or ""
        by_number = operators.config.canonical_ordinal_suffix_by_number or {}
        by_ending = sorted(
            (operators.config.canonical_ordinal_suffix_by_ending or {}).items(),
            key=lambda item: len(item[0]),
            reverse=True,
        )

        def _suffix(digits: str) -> str:
            if digits in by_number:
                return by_number[digits]
            for ending, suffix in by_ending:
                if digits.endswith(ending):
                    return suffix
            return default

        def _restore(match: re.Match) -> str:
            digits = ordinal_placeholder_digits(match.group(1))
            return digits + _suffix(digits)

        return _RE_ORDINAL_PLACEHOLDER.sub(_restore, text)
