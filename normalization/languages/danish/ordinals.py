"""Danish ordinal data: the suffixes of a digit ordinal (1ste, 2en, 3dje, 20ende).

The spelled ordinals (første, tyvende) are read by the number normalizer, which writes
them as the bare number; a digit ordinal loses its suffix to meet them.
"""

ORDINAL_SUFFIXES: list[str] = ["ste", "te", "en", "den", "dje", "de", "ende"]
