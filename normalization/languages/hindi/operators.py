import re

from words2num2 import words2num_sentence

from normalization.languages.base import LanguageConfig, LanguageOperators
from normalization.languages.hindi.replacements import HINDI_REPLACEMENTS
from normalization.languages.registry import register_language

# Devanagari digits ० to ९ (U+0966-U+096F) become ASCII so that every numeric
# step sees them, and "२५" scores like "25".
_DEVANAGARI_ZERO = 0x0966
_DIGITS: dict[str, str] = {chr(_DEVANAGARI_ZERO + d): str(d) for d in range(10)}

_NUKTA = "़"

# The five letters that take a nukta for Urdu (Perso-Arabic) sounds, in their
# precomposed code points. The standard orthography of the Central Hindi
# Directorate (rule 3.15.1) writes the Urdu words Hindi has absorbed without the
# nukta, so "ज़मीन" and "जमीन" are one word. ड़ and ढ़ are not in this list:
# they are letters of the Hindi alphabet, and "पढ़ा" is not "पढा".
_URDU_NUKTA_LETTERS: dict[str, str] = {
    "क़": "क",  # क़
    "ख़": "ख",  # ख़
    "ग़": "ग",  # ग़
    "ज़": "ज",  # ज़
    "फ़": "फ",  # फ़
}
# The same letters written as base letter + nukta (U+093C).
_RE_URDU_NUKTA = re.compile(f"([{''.join(_URDU_NUKTA_LETTERS.values())}]){_NUKTA}")

_VIRAMA = "्"
_ANUSVARA = "ं"
_CHANDRABINDU = "ँ"

# A nasal consonant with virama before a consonant of its own class is written
# as anusvara (rule 3.6.1.2: पंकज, गंगा, चंचल, कंठ, संत, संपादक). Before a
# consonant of another class, or doubled, it stays (rules 3.6.1.3 and 3.6.1.4:
# अन्य, उन्मुख, अन्न, सम्मेलन): the lookahead only accepts its own class.
_NASAL_CLASSES: dict[str, str] = {
    "ङ": "कखगघ",
    "ञ": "चछजझ",
    "ण": "टठडढ",
    "न": "तथदध",
    "म": "पफबभ",
}
_RE_NASAL_CONJUNCT = re.compile(
    "|".join(f"{nasal}{_VIRAMA}(?=[{cls}])" for nasal, cls in _NASAL_CLASSES.items())
)

# Chandrabindu (nasal vowel) is folded into anusvara: newspapers, magazines and
# even textbooks write anusvara in its place (rule 3.6.2.5), so "चाँद" / "चांद"
# and "यहाँ" / "यहां" are one word. Rule 3.6.2.3 names the pairs where the two
# signs make different words: हंस "swan" / हँस "laugh", अंगना "woman" / अँगना
# "courtyard". A word starting with one of these chandrabindu stems keeps it.
_CHANDRABINDU_KEPT_STEMS = ("हँस", "अँगन")
_RE_DEVANAGARI_WORD = re.compile(r"[ऀ-ॿ]+")

HINDI_CONFIG = LanguageConfig(
    code="hi",
    # Email and technical symbols are read as the English words; "%" is
    # प्रतिशत, the word Hindi writes after a number ("50 प्रतिशत").
    symbols_to_words={
        "@": "एट",
        ".": "डॉट",
        "+": "प्लस",
        "%": "प्रतिशत",
    },
    character_replacements={**_DIGITS, **_URDU_NUKTA_LETTERS},
)


def _fold_chandrabindu(match: re.Match[str]) -> str:
    word = match.group(0)
    if word.startswith(_CHANDRABINDU_KEPT_STEMS):
        return word
    return word.replace(_CHANDRABINDU, _ANUSVARA)


@register_language
class HindiOperators(LanguageOperators):
    def __init__(self) -> None:
        super().__init__(HINDI_CONFIG)
        self._digits = str.maketrans(_DIGITS)

    def normalize_spelling_variants(self, text: str) -> str:
        """Fold nukta, nasal conjuncts and chandrabindu (ज़मीन -> जमीन, केन्द्र -> केंद्र, चाँद -> चांद)."""
        text = _RE_URDU_NUKTA.sub(r"\1", text)
        text = _RE_NASAL_CONJUNCT.sub(_ANUSVARA, text)
        return _RE_DEVANAGARI_WORD.sub(_fold_chandrabindu, text)

    def expand_written_numbers(self, text: str) -> str:
        """Convert spelled-out Hindi numbers to digits (पच्चीस -> 25, तीन सौ पचास -> 350).

        words2num2 writes ordinals with Devanagari digits ("तीसरा" -> "३रा"):
        they are turned to ASCII like the digits of the input.
        """
        return words2num_sentence(text, lang=HINDI_CONFIG.code).translate(self._digits)

    def get_word_replacements(self) -> dict[str, str]:
        return HINDI_REPLACEMENTS
