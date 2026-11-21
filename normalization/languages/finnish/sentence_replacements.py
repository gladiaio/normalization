"""Sentence-level replacements for colloquial Finnish.

``apply_sentence_level_replacements`` runs before ``casefold_text`` and
``remove_diacritics`` in the gladia-3 preset, so keys here are matched against
the not-yet-stripped surface form (matching is IGNORECASE and word-bounded).
"""

FINNISH_SENTENCE_REPLACEMENTS: dict[str, str] = {
    # Colloquial "oo" ("is/am") -> standard "ole". Must run BEFORE
    # remove_diacritics / remove_filler_words: the filler "öö" is folded to
    # "oo" when the operators are built and would otherwise be indistinguishable
    # from the genuine verb at filler-matching time. At sentence-replacement
    # time the filler is still "öö" — a form the "oo" key cannot match — so
    # real "oo" keeps mapping to "ole" while "öö" is removed later by
    # remove_filler_words (issue #54).
    "oo": "ole",
}
