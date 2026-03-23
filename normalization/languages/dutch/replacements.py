"""Single-token Flemish / colloquial → standard Dutch (canonical for WER)."""

DUTCH_REPLACEMENTS: dict[str, str] = {
    "ge": "je",
    "da": "dat",
    "ne": "een",
    "efkes": "even",
    "effe": "even",
    "awel": "wel",
    "den": "de",
    "mijne": "mijn",
    "gij": "jij",
}
