"""Colloquial / spoken variants → standard Finnish (canonical for WER).

Keys and values use the same ASCII-folded surface form as the rest of the gladia-3
pipeline after ``casefold_text`` and ``remove_diacritics``.
"""

FINNISH_REPLACEMENTS: dict[str, str] = {
    "ma": "mina",
    "maa": "mina",
    "mulle": "minulle",
    "mulla": "minulla",
    "mua": "minua",
    "mun": "minun",
    "sa": "sina",
    "sulle": "sinulle",
    "sulla": "sinulla",
    "sua": "sinua",
    "sun": "sinun",
    "toi": "tuo",
    "ton": "tuon",
    "tossa": "tuossa",
    "tosta": "tuosta",
    "tohon": "tuohon",
    "taa": "tama",
    "naa": "nama",
    "olis": "olisi",
    "ois": "olisi",
    # "oo" -> "ole" lives in sentence_replacements.py instead: it must be applied
    # before remove_diacritics / remove_filler_words, otherwise the filler "öö"
    # (folded to "oo" at operator build time) would swallow the genuine
    # colloquial verb "oo" before the replacement could map it to "ole".
    "ollu": "ollut",
    "onks": "onko",
    "oliks": "oliko",
    "oisko": "olisiko",
    "vois": "voisi",
    "katotaan": "katsotaan",
    "kattoa": "katsoa",
    "mut": "mutta",
    "sit": "sitten",
    "sitte": "sitten",
    "et": "etta",
    "sillon": "silloin",
    "viimeks": "viimeksi",
    "elikka": "eli",
    "juu": "joo",
    "jes": "joo",
    "ok": "okei",
    "bank": "pankki",
    "bankin": "pankin",
    "euro": "euros",
}
