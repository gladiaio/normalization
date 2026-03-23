"""Single-token Flemish / colloquial → standard Dutch (canonical for WER)."""

DUTCH_REPLACEMENTS: dict[str, str] = {
    # Flemish dialect → standard Dutch
    "ge": "je",
    "da": "dat",
    "ne": "een",
    "efkes": "even",
    "effe": "even",
    "awel": "wel",
    "den": "de",
    "mijne": "mijn",
    "gij": "jij",
    "zij": "ze",
    "zijne": "zijn",
    # Bare clitics (apostrophe dropped by ASR)
    "t": "het",
    "s": "is",
    "r": "er",
    "k": "ik",
    # Formal / informal pronoun conflation (Flemish customer service)
    # ref uses formal u/uw; models transcribe je — normalise to je
    "u": "je",
    "uw": "je",
    # Spelling variants → canonical
    "okee": "oke",  # oke is already in filler_words; okee must map to it
    "euro": "euros",  # collapse singular/plural
}
