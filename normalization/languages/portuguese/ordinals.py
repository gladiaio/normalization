"""Portuguese ordinal data: digit marks (1º, 1ª, 1.º) and the spelled ordinals the number
normalizer leaves as words.

Every ordinal is written as its number plus "º", masculine and feminine alike: the
spelled form, "1º", "1.º" and "1ª" all become "1º". The number normalizer writes
"terceira" as "3ª". "segundo/segunda" (also the time unit and Monday,
"segunda-feira") are left out.
"""

ORDINAL_SUFFIXES: list[str] = ["º", "ª", ".º", ".ª"]

CANONICAL_SUFFIX = "º"

SPELLED_ORDINALS: dict[str, str] = {
    "primeiro": "1",
    "primeira": "1",
    "primeiros": "1",
    "primeiras": "1",
}
