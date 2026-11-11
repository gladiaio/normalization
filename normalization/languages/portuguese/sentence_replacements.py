"""Multi-word Portuguese phrase normalization (oral variants, compounds, ASR repairs)."""

PORTUGUESE_SENTENCE_REPLACEMENTS: dict[str, str] = {
    # Email compounds (hyphenated forms run in text_pre; spaced forms after cleanup)
    "e-mails": "email",
    "e-mail": "email",
    "e mail": "email",
    "e mails": "email",
    # Clitic spacing (ASR splits glued imperatives)
    "envie me": "enviame",
    "diga me": "digame",
    "fale me": "faleme",
}
