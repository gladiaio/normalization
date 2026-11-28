"""Dutch ordinal data: digit suffixes (1ste, 2de, 3e) and the spelled ordinals the number
normalizer leaves as words.

Every ordinal normalizes to the bare number: the number normalizer writes "vierde" as
"4e", whose suffix is then dropped; "eerste" and "tweede" are the ones it does not read.
"""

ORDINAL_SUFFIXES: list[str] = ["ste", "de", "e"]

SPELLED_ORDINALS: dict[str, str] = {
    "eerste": "1",
    "tweede": "2",
}
