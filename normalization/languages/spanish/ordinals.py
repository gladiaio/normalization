"""Spanish ordinal data: digit marks (1º, 1ª, 1.º, 1.er) and spelled ordinals.

Every ordinal is written as its number plus "º", masculine and feminine alike: the
spelled form, "1º", "1.º" and "1ª" all become "1º". "1er", "1.er" and "3er" (primer,
tercer) become "1º" and "3º". "segundo" (also the time unit, "un segundo")
and "cuarto" (also a room and a quarter, "un cuarto de hora") are left out.
"""

ORDINAL_SUFFIXES: list[str] = [
    "º",
    "ª",
    ".º",
    ".ª",
    ".er",
    "er",
]

CANONICAL_SUFFIX = "º"

# Each stem takes the four endings o, a, os, as ("quinto", "quinta", "quintos", "quintas").
_STEMS: dict[str, int] = {
    "primer": 1,
    "tercer": 3,
    "quint": 5,
    "sext": 6,
    "séptim": 7,
    "sétim": 7,
    "octav": 8,
    "noven": 9,
    "décim": 10,
}

SPELLED_ORDINALS: dict[str, str] = {
    **{
        stem + ending: str(value)
        for stem, value in _STEMS.items()
        for ending in ("o", "a", "os", "as")
    },
    "primer": "1",
    "tercer": "3",
    "segunda": "2",
    "segundas": "2",
    "cuarta": "4",
    "cuartas": "4",
}
