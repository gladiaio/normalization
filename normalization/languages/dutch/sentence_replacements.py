"""Multi-word and phrase-level normalization for Dutch (incl. Flemish variants)."""

DUTCH_SENTENCE_REPLACEMENTS: dict[str, str] = {
    "fifty fifty": "5050",
    "fiftyfifty": "5050",
    "checks": "cheques",
    "goeiemiddag": "goedemiddag",
    "kollega": "collega",
}
