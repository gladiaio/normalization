"""Single-token Portuguese colloquial / ASR variants → canonical form for WER."""

PORTUGUESE_REPLACEMENTS: dict[str, str] = {
    # Oral preposition / contraction variants
    "pra": "para",
    # Email spelling
    "emails": "email",
    # PT-PT / PT-BR orthography (canonical: PT-PT)
    "controles": "controlos",
    "equipe": "equipa",
    # Clitic / verb form variants (ASR subjunctive vs imperative)
    "envieme": "enviame",
    # Abbreviations / titles
    "dr": "doutor",
    "dra": "doutora",
    "sr": "senhor",
    "sra": "senhora",
    "exmo": "excelentissimo",
    "exma": "excelentissima",
    "etc": "etcetera",
    "tel": "telefone",
    # Acknowledgments / spelling variants
    "okay": "ok",
}
