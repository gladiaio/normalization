"""Dutch ordinal data: digit suffixes (1ste, 2de, 3e) and the spelled ordinals the number
normalizer leaves as words.

Every ordinal is written as its number plus "e": "eerste", "1ste" and "1e" all become
"1e". The number normalizer writes "vierde" as "4e"; "eerste" and "tweede" are the ones
it does not read.
"""

ORDINAL_SUFFIXES: list[str] = ["ste", "de", "e"]

CANONICAL_SUFFIX = "e"

SPELLED_ORDINALS: dict[str, str] = {
    "eerste": "1",
    "tweede": "2",
}
