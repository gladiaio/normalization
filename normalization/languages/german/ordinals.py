"""German ordinal data: digit suffixes (1te, 1ten, 20sten) and the spelled ordinals the
number normalizer leaves as words.

Every ordinal is written as its number plus ".", the German ordinal mark: "ersten",
"1ten" and "1." all become "1.". The number normalizer writes "dritten" as "3.";
"erst-" and "zweit-" are the two it does not read. "Erstens" (firstly) is left out.
"." only counts before another word (see protect_digit_ordinals).
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
    ".",
]

CANONICAL_SUFFIX = "."

_ENDINGS: tuple[str, ...] = ("e", "en", "er", "es", "em")

SPELLED_ORDINALS: dict[str, str] = {
    **{"erst" + ending: "1" for ending in _ENDINGS},
    **{"zweit" + ending: "2" for ending in _ENDINGS},
}
