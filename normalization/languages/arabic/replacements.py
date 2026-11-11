"""Word-level substitutions for Arabic.

Word replacements run after every text_pre step, so keys and values must use
the normalized surface form: no harakat or tatweel, bare alef for أ/إ/آ/ٱ,
و for ؤ, ي for ئ and ى, ه for ة (see ``character_replacements`` in
``operators.py``). A key spelled with any of the folded letters never matches.
"""

ARABIC_REPLACEMENTS: dict[str, str] = {}
