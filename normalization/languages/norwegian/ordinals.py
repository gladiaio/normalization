"""Norwegian ordinal data: digit suffixes (1ste, 2dre, 3dje, 20ende) and spelled ordinals.

Both forms normalize to the bare number, as "1." already does. "andre" (second) is left
out: it is also "other" ("de andre barna"), so folding it would turn "other" into 2.
"""

ORDINAL_SUFFIXES: list[str] = ["ste", "dre", "dje", "je", "de", "te", "ende"]

_ONES: dict[str, int] = {
    "første": 1,
    "tredje": 3,
    "fjerde": 4,
    "femte": 5,
    "sjette": 6,
    "sjuende": 7,
    "syvende": 7,
    "åttende": 8,
    "niende": 9,
}

_TEENS: dict[str, int] = {
    "tiende": 10,
    "ellevte": 11,
    "tolvte": 12,
    "trettende": 13,
    "fjortende": 14,
    "femtende": 15,
    "sekstende": 16,
    "syttende": 17,
    "attende": 18,
    "nittende": 19,
}

# Tens as the prefix of a compound ("tjueførste") and as an ordinal on their own ("tjuende").
_TENS: dict[str, tuple[int, str]] = {
    "tjue": (20, "tjuende"),
    "tretti": (30, "trettiende"),
    "førti": (40, "førtiende"),
    "femti": (50, "femtiende"),
    "seksti": (60, "sekstiende"),
    "sytti": (70, "syttiende"),
    "åtti": (80, "åttiende"),
    "nitti": (90, "nittiende"),
}

# In a compound "andre" is only "second": "tjueandre" is the 22nd.
_COMPOUND_ONES: dict[str, int] = {**_ONES, "andre": 2}

SPELLED_ORDINALS: dict[str, str] = {
    **{word: str(value) for word, value in {**_ONES, **_TEENS}.items()},
    "tyvende": "20",
    "hundrede": "100",
    **{ordinal: str(value) for value, ordinal in _TENS.values()},
    **{
        prefix + ones: str(tens + value)
        for prefix, (tens, _) in _TENS.items()
        for ones, value in _COMPOUND_ONES.items()
    },
}
