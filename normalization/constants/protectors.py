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
    # Comma between multi-digit numbers ("60, 70"), and the edges of an ordinal
    # (fr "premier 93" -> "¶ 1 ¶ 93"): kept until after digit collapsing so the
    # numbers are not glued into "6070" or "193", then restored as space.
    NUMBER_LIST_COMMA = "¶"
    SPELLING_SUFFIX = "xltrx"


# An ordinal written as digits ("premier" -> "1", "1er" -> "1") between two
# NUMBER_LIST_COMMA marks: it stays one number, apart from a number next to it.
SEPARATE_NUMBER_TEMPLATE = (
    f"{ProtectPlaceholder.NUMBER_LIST_COMMA.value} {{}} "
    f"{ProtectPlaceholder.NUMBER_LIST_COMMA.value}"
)


PLACEHOLDER_FALLBACK_CHARS: dict[str, str] = {
    ProtectPlaceholder.EMAIL_AT: "@",
    ProtectPlaceholder.EMAIL_DOT: ".",
    ProtectPlaceholder.PHONE_PLUS: "+",
    ProtectPlaceholder.TIME_COLON: ":",
    ProtectPlaceholder.UNIT_SLASH: "/",
    ProtectPlaceholder.UNIT_DECIMAL: ".",
    ProtectPlaceholder.DECIMAL_SEPARATOR: ".",
}
