"""Portuguese ordinal data: digit marks (1º, 1ª, 1.º) and the spelled ordinals the number
normalizer leaves as words.

Every ordinal normalizes to the bare number: the number normalizer writes "terceira" as
"3ª", whose mark is then dropped. "segundo/segunda" (also the time unit and Monday,
"segunda-feira") are left out.
"""

ORDINAL_SUFFIXES: list[str] = ["º", "ª", ".º", ".ª"]

SPELLED_ORDINALS: dict[str, str] = {
    "primeiro": "1",
    "primeira": "1",
    "primeiros": "1",
    "primeiras": "1",
}
