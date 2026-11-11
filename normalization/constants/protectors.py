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
