"""Swedish ordinal data: digit suffixes (1:a, 3:e) and spelled ordinals (första, tjugonde).

Every ordinal is written with the standard Swedish suffix: ":a" after 1 and 2 (not 11
and 12), ":e" otherwise. "första" and "1:a" become "1:a"; "tredje", "3:e" and "3:a"
become "3:e". "andra" and "andre" (second) are left out: they
are also "other" ("de andra barnen"), so folding them would turn "other" into 2.
"""

ORDINAL_SUFFIXES: list[str] = [":a", ":e"]

# The Swedish rule: ":a" after 1 and 2 (1:a, 22:a), but ":e" after 11 and 12, and
# after every other number (3:e, 11:e).
CANONICAL_SUFFIX = ":e"

CANONICAL_SUFFIX_BY_ENDING: dict[str, str] = {
    "1": ":a",
    "2": ":a",
    "11": ":e",
    "12": ":e",
}

_ONES: dict[str, int] = {
    "första": 1,
    "förste": 1,
    "tredje": 3,
    "fjärde": 4,
    "femte": 5,
    "sjätte": 6,
    "sjunde": 7,
    "åttonde": 8,
    "nionde": 9,
}

_TEENS: dict[str, int] = {
    "tionde": 10,
    "elfte": 11,
    "tolfte": 12,
    "trettonde": 13,
    "fjortonde": 14,
    "femtonde": 15,
    "sextonde": 16,
    "sjuttonde": 17,
    "artonde": 18,
    "nittonde": 19,
}

# Tens as the prefix of a compound ("tjugoförsta") and as an ordinal on their own ("tjugonde").
_TENS: dict[str, tuple[int, str]] = {
    "tjugo": (20, "tjugonde"),
    "trettio": (30, "trettionde"),
    "fyrtio": (40, "fyrtionde"),
    "femtio": (50, "femtionde"),
    "sextio": (60, "sextionde"),
    "sjuttio": (70, "sjuttionde"),
    "åttio": (80, "åttionde"),
    "nittio": (90, "nittionde"),
}

# In a compound "andra" is only "second": "tjugoandra" is the 22nd.
_COMPOUND_ONES: dict[str, int] = {**_ONES, "andra": 2, "andre": 2}

SPELLED_ORDINALS: dict[str, str] = {
    **{word: str(value) for word, value in {**_ONES, **_TEENS}.items()},
    "hundrade": "100",
    **{ordinal: str(value) for value, ordinal in _TENS.values()},
    **{
        prefix + ones: str(tens + value)
        for prefix, (tens, _) in _TENS.items()
        for ones, value in _COMPOUND_ONES.items()
    },
}
