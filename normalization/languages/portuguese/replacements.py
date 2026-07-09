"""Single-token Portuguese colloquial / ASR variants → canonical form for WER."""

PORTUGUESE_REPLACEMENTS: dict[str, str] = {
    # Oral preposition / contraction variants
    "pra": "para",
    # Gender agreement in short confirmations (telephony slips)
    "propria": "proprio",
    "proprias": "proprios",
    # Adjective / adverb spelling variants
    "maioritariamente": "maioritario",
    "media": "medio",
    # Email / compound spelling
    "emails": "email",
    "e-mail": "email",
    "e-mails": "email",
    # Morphological number (singular/plural oral agreement)
    "rotativos": "rotativo",
    "turnos": "turno",
    "pesos": "peso",
    "quantos": "quanto",
    # PT-PT / PT-BR orthography (canonical: PT-PT)
    "controles": "controlos",
    "equipe": "equipa",
    "confirmar-se": "confirmares",
    # Clitic / verb form variants (ASR subjunctive vs imperative)
    "envieme": "enviame",
    "adeco": "adecco",
    "adec": "adecco",
    # Abbreviations / titles
    "dr": "doutor",
    "dra": "doutora",
    "sr": "senhor",
    "sra": "senhora",
    "exmo": "excelentissimo",
    "exma": "excelentissima",
    "etc": "etcetera",
    "tel": "telefone",
    "vs": "versus",
    "versus": "versus",
    # Acknowledgments / spelling variants
    "okay": "ok",
}
