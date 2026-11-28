"""German ordinal data: digit suffixes (1te, 1ten, 20sten) and the spelled ordinals the
number normalizer leaves as words.

Every ordinal normalizes to the bare number, as "1." and "dritten" already do; "erst-" and
"zweit-" are the two the number normalizer does not read. "Erstens" (firstly) is left out.
"""

ORDINAL_SUFFIXES: list[str] = [
    "te",
    "ten",
    "ter",
    "tes",
    "tem",
    "ste",
    "sten",
    "ster",
    "stes",
    "stem",
]

_ENDINGS: tuple[str, ...] = ("e", "en", "er", "es", "em")

SPELLED_ORDINALS: dict[str, str] = {
    **{"erst" + ending: "1" for ending in _ENDINGS},
    **{"zweit" + ending: "2" for ending in _ENDINGS},
}
