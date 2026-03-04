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
    SPELLING_SUFFIX = "xltrx"
