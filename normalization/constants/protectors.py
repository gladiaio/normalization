from enum import Enum


class ProtectPlaceholder(str, Enum):
    DECIMAL_SEPARATOR = "XDECIMALX"
    EMAIL_AT = "XATX"
    EMAIL_DOT = "XDOTX"
    PHONE_PLUS = "XPLUSX"
    TIME_COLON = "§"
    UNIT_SLASH = "†"
    UNIT_DECIMAL = "‡"
    NUMBER_SEPARATOR = "¤"
    # Comma between multi-digit numbers ("60, 70"): kept until after digit
    # collapsing so the groups are not glued into "6070", then restored as space.
    NUMBER_LIST_COMMA = "¶"
    SPELLING_SUFFIX = "xltrx"


PLACEHOLDER_FALLBACK_CHARS: dict[str, str] = {
    ProtectPlaceholder.EMAIL_AT: "@",
    ProtectPlaceholder.EMAIL_DOT: ".",
    ProtectPlaceholder.PHONE_PLUS: "+",
    ProtectPlaceholder.TIME_COLON: ":",
    ProtectPlaceholder.UNIT_SLASH: "/",
    ProtectPlaceholder.UNIT_DECIMAL: ".",
    ProtectPlaceholder.DECIMAL_SEPARATOR: ".",
}


# An ordinal ("premier", "1er", "første", "1:a") held until the end of the pipeline,
# where restore_ordinals writes it as digits plus the language's canonical suffix
# ("1er", "1.", "1:a"). The token is letters only: its digits are spelled with
# ORDINAL_DIGIT_LETTERS, so no digit step glues it to a number next to it, and
# expand_alphanumeric_codes, remove_symbols and remove_diacritics leave it whole.
# It is not a ProtectPlaceholder member: remove_symbols keeps every character of
# those, and gladia-3's output must not change.
ORDINAL_PLACEHOLDER_PREFIX = "xordx"
ORDINAL_PLACEHOLDER_END = "x"
ORDINAL_DIGIT_LETTERS = "abcdefghij"
_DIGITS_TO_LETTERS = str.maketrans("0123456789", ORDINAL_DIGIT_LETTERS)
_LETTERS_TO_DIGITS = str.maketrans(ORDINAL_DIGIT_LETTERS, "0123456789")


def ordinal_placeholder(digits: str) -> str:
    """'21' -> 'xordxcbx': the placeholder of the ordinal whose number is ``digits``."""
    return (
        f"{ORDINAL_PLACEHOLDER_PREFIX}{digits.translate(_DIGITS_TO_LETTERS)}"
        f"{ORDINAL_PLACEHOLDER_END}"
    )


def ordinal_placeholder_digits(letters: str) -> str:
    """'cb' -> '21': the number held by an ordinal placeholder's letters."""
    return letters.translate(_LETTERS_TO_DIGITS)
