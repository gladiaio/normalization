"""Italian ordinal data: digit marks (1º, 1ª) and the spelled ordinals the number
normalizer leaves as words.

Every ordinal is written as its number plus "º", masculine and feminine alike: the
spelled form, "1º", "1.º" and "1ª" all become "1º". The number normalizer writes
"terza" as "3ª". "prima/prime" (also "before") and "secondo/seconda/secondi"
(also "according to" and the time unit) are left out.
"""

ORDINAL_SUFFIXES: list[str] = ["º", "ª", ".º", ".ª"]

CANONICAL_SUFFIX = "º"

SPELLED_ORDINALS: dict[str, str] = {
    "primo": "1",
    "primi": "1",
}
