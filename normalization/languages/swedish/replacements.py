"""Single-token colloquial / spelling variants → standard Swedish (canonical for WER)."""

SWEDISH_REPLACEMENTS: dict[str, str] = {
    "mej": "mig",
    "dej": "dig",
    "dom": "de",
    "nåt": "något",
    "nånting": "någonting",
    "sån": "sådan",
    "sånt": "sådant",
    "såna": "sådana",
    "euro": "euros",
    "krona": "kronor",
}
