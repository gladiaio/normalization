import re

from words2num2 import words2num_sentence

from normalization.languages.base import LanguageConfig, LanguageOperators
from normalization.languages.bengali.replacements import BENGALI_REPLACEMENTS
from normalization.languages.registry import register_language

# Bengali digits ০ to ৯ (U+09E6-U+09EF) become ASCII so that every numeric step
# sees them, and "২৫" scores like "25".
_BENGALI_ZERO = 0x09E6
_DIGITS: dict[str, str] = {chr(_BENGALI_ZERO + d): str(d) for d in range(10)}

_VIRAMA = "্"
_ANUSVARA = "ং"

# ঙ with virama before ক খ গ ঘ is written as anusvara too: the Bangla Academy
# standard spelling rules write ং in sandhi words (অহংকার, সংগীত, ভয়ংকর) and ঙ
# in the others (অঙ্ক, গঙ্গা, সঙ্গে), and both spellings are in use for both
# kinds. The two signs are the same sound before a velar, so the fold merges no
# two words. Chandrabindu is not folded: unlike Hindi, no Bengali standard
# treats it as a variant of anusvara.
_RE_NASAL_CONJUNCT = re.compile(f"ঙ{_VIRAMA}(?=[কখগঘ])")

# words2num2 reads the hundreds written "শত" glued to their count ("তিনশত" ->
# 300), not the spoken "শ" / "শো" ("তিনশো", "তিন শো"). These are rewritten
# to the "শত" form first. "দু" and "ছ" are the short forms of দুই and ছয়.
_HUNDRED_COUNTS: dict[str, str] = {
    "এক": "এক",
    "দুই": "দুই",
    "দু": "দুই",
    "তিন": "তিন",
    "চার": "চার",
    "পাঁচ": "পাঁচ",
    "ছয়": "ছয়",
    "ছ": "ছয়",
    "সাত": "সাত",
    "আট": "আট",
    "নয়": "নয়",
}
_HUNDRED = "শত"
_RE_SPOKEN_HUNDRED = re.compile(
    r"(?<![ঀ-৿])("
    + "|".join(sorted(_HUNDRED_COUNTS, key=lambda word: -len(word)))
    + r")(?:শো|শ| শো)(?![ঀ-৿])"
)

BENGALI_CONFIG = LanguageConfig(
    code="bn",
    # Email and technical symbols are read as the English words; "%" is
    # শতাংশ, the word Bengali writes after a number ("৫০ শতাংশ").
    symbols_to_words={
        "@": "অ্যাট",
        ".": "ডট",
        "+": "প্লাস",
        "%": "শতাংশ",
    },
    character_replacements=_DIGITS,
)


@register_language
class BengaliOperators(LanguageOperators):
    def __init__(self) -> None:
        super().__init__(BENGALI_CONFIG)
        self._digits = str.maketrans(_DIGITS)

    def normalize_spelling_variants(self, text: str) -> str:
        """Fold ঙ + virama before a velar into anusvara (অহঙ্কার -> অহংকার)."""
        return _RE_NASAL_CONJUNCT.sub(_ANUSVARA, text)

    def expand_written_numbers(self, text: str) -> str:
        """Convert spelled-out Bengali numbers to digits (পঁচিশ -> 25, তিনশো পঞ্চাশ -> 350).

        words2num2 writes ordinals with Bengali digits ("তৃতীয়" -> "৩য়"): they
        are turned to ASCII like the digits of the input.
        """
        text = _RE_SPOKEN_HUNDRED.sub(
            lambda m: f"{_HUNDRED_COUNTS[m.group(1)]}{_HUNDRED}", text
        )
        return words2num_sentence(text, lang=BENGALI_CONFIG.code).translate(
            self._digits
        )

    def get_word_replacements(self) -> dict[str, str]:
        return BENGALI_REPLACEMENTS
