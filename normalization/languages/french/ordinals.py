"""French ordinal data: digit suffixes (1er, 1re, 2e, 2ème, 2nd) and the spelled ordinals
the number normalizer leaves as words.

Every ordinal normalizes to the bare number: the number normalizer writes "cinquième" as
"5ème", whose suffix is then dropped. "second(e)" is left out: it is also the time unit
("une seconde").
"""

ORDINAL_SUFFIXES: list[str] = [
    "er",
    "ers",
    "re",
    "res",
    "ère",
    "ères",
    "e",
    "es",
    "ème",
    "èmes",
    "eme",
    "emes",
    "nd",
    "nds",
    "nde",
    "ndes",
]

SPELLED_ORDINALS: dict[str, str] = {
    "premier": "1",
    "premiers": "1",
    "première": "1",
    "premières": "1",
    "deuxième": "2",
    "deuxièmes": "2",
    "troisième": "3",
    "troisièmes": "3",
}
