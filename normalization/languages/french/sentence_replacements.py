FRENCH_SENTENCE_REPLACEMENTS: dict[str, str] = {
    "super predateur": "superprédateur",
    "ping pong": "pingpong",
    "hand ball": "handball",
    "water polo": "waterpolo",
    "basket ball": "basketball",
    "volley ball": "volleyball",
    "wi fi": "wifi",
    "cd rom": "cdrom",
    "t shirt": "tshirt",
    "pour 100": "pourcent",
    "pour cent": "pourcent",
    # ASR / WER canonicalizations
    "my people doc": "mypeopledoc",
    "releve d heure": "releve d heures",
    # Surface area: converge spoken form and symbol (not bare ``metres``).
    # apply_sentence_level_replacements runs before remove_diacritics, so both
    # accented and ASCII forms must be listed (IGNORECASE covers casing only).
    "mètres carrés": "m2",
    "mètre carré": "m2",
    "mètres carré": "m2",
    "metres carres": "m2",
    "metre carre": "m2",
    "metres carre": "m2",
}
