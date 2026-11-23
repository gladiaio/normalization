"""Word-level substitutions for Japanese.

Japanese is written without spaces, so a word-level replacement only matches a
whole space-separated run of text. None is needed yet: the numeral forms are
handled by ``number_normalizer.py``.
"""

JAPANESE_REPLACEMENTS: dict[str, str] = {}
