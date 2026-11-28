"""Italian ordinal data: digit marks (1º, 1ª) and the spelled ordinals the number
normalizer leaves as words.

Every ordinal normalizes to the bare number: the number normalizer writes "terza" as "3ª",
whose mark is then dropped. "prima/prime" (also "before") and "secondo/seconda/secondi"
(also "according to" and the time unit) are left out.
"""

ORDINAL_SUFFIXES: list[str] = ["º", "ª", ".º", ".ª"]

SPELLED_ORDINALS: dict[str, str] = {
    "primo": "1",
    "primi": "1",
}
