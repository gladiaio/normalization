"""Multi-word Portuguese phrase normalization (oral variants, compounds, ASR repairs)."""

PORTUGUESE_SENTENCE_REPLACEMENTS: dict[str, str] = {
    # Email compounds (hyphenated forms run in text_pre; spaced forms after cleanup)
    "e-mails": "email",
    "e-mail": "email",
    "e mail": "email",
    "e mails": "email",
    # Morphological number / construction variants
    "turnos rotativos": "turno rotativo",
    "em quantos pesos": "de quanto peso",
    # PT-PT / PT-BR orthography
    "confirmar se": "confirmares",
    # Clitic spacing (ASR splits glued imperatives)
    "envie me": "enviame",
    "diga me": "digame",
}
