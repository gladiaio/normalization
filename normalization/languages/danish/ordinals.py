"""Danish ordinal data: the suffixes of a digit ordinal (1ste, 2en, 3dje, 20ende, 1.).

Every ordinal is written as its number plus ".", the Danish ordinal mark: "første",
"1ste" and "1." all become "1.". The spelled ordinals (første, tyvende) are read by the
number normalizer. "." only counts before another word (see protect_digit_ordinals).
"""

ORDINAL_SUFFIXES: list[str] = ["ste", "te", "en", "den", "dje", "de", "ende", "."]

CANONICAL_SUFFIX = "."
