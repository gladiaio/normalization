"""Japanese script fold for scoring: hiragana and katakana, 々, trailing ー, ヶ/ヵ.

The same word is often written in hiragana or in katakana (ころころ / コロコロ),
a kanji is repeated with the iteration mark 々 or written twice (人々 / 人人), a
loanword ends with or without its long-vowel mark (コンピューター /
コンピュータ), and the counter か is written ヶ, ヵ or か (3ヶ月 / 3か月). Each pair
is one word, so this fold gives both forms the same string. Its output is for
scoring only, never for display.

Sources:
- Katakana U+30A1–U+30F6 and hiragana U+3041–U+3096 are the same syllables
  (The Unicode Standard, chapter 18.4) and share character names at an offset
  of 0x60 (UnicodeData.txt); ヷ ヸ ヹ ヺ (U+30F7–U+30FA) have no hiragana.
- 外来語の表記 (1991 cabinet notice), 留意事項その2 III-3 注3: a final -er, -or,
  -ar is written with ー, "ただし、慣用に応じて「ー」を省くことができる"
  (コンピューター / コンピュータ).
- 公用文作成の考え方 (2022), I-4 ケ: the counter is written 3か所, 7か月 with
  digits and 三箇所, 七箇月 with kanji; 3ヶ所, 7カ月 are the everyday variants.
"""

from __future__ import annotations

import re
import unicodedata

# Katakana letters that have a hiragana at KATAKANA_TO_HIRAGANA_OFFSET below.
KATAKANA_FIRST = 0x30A1  # ァ
KATAKANA_LAST = 0x30F6  # ヶ
KATAKANA_TO_HIRAGANA_OFFSET = 0x60
# ヷ ヸ ヹ ヺ: katakana only, kept as written.
KATAKANA_ONLY_FIRST = 0x30F7
KATAKANA_ONLY_LAST = 0x30FA
PROLONGED_SOUND_MARK = "ー"  # ー
IDEOGRAPHIC_ITERATION_MARK = "々"  # 々
# CJK Unified Ideographs and Extension A: the kanji a 々 can repeat.
KANJI_RANGES = ((0x4E00, 0x9FFF), (0x3400, 0x4DBF))
# The counter か and its variants after a number: ヵ ヶ (katakana), ゕ ゖ
# (their hiragana) and 箇 (its kanji, 三箇所).
COUNTER_KA = "か"
COUNTER_KA_VARIANTS = "ヵヶゕゖ箇"
# What a counter follows: digits, kanji numerals and 数 何 幾 (数箇所, 何か月).
_NUMBER_BEFORE_COUNTER = "0-9０-９〇一二三四五六七八九十百千万億兆数何幾"

_KATAKANA_LETTERS = (
    f"{chr(KATAKANA_FIRST)}-{chr(KATAKANA_ONLY_LAST)}{PROLONGED_SOUND_MARK}"
)
# A run of ー that ends a katakana word: after a katakana letter, not before one.
_TRAILING_PROLONGED_MARK = re.compile(
    rf"(?<=[{chr(KATAKANA_FIRST)}-{chr(KATAKANA_ONLY_LAST)}])"
    rf"{PROLONGED_SOUND_MARK}+(?![{_KATAKANA_LETTERS}])"
)
_COUNTER = re.compile(rf"(?<=[{_NUMBER_BEFORE_COUNTER}])[{COUNTER_KA_VARIANTS}]")
_KATAKANA_TO_HIRAGANA = {
    code: code - KATAKANA_TO_HIRAGANA_OFFSET
    for code in range(KATAKANA_FIRST, KATAKANA_LAST + 1)
}


def _is_kanji(character: str) -> bool:
    code = ord(character)
    return any(first <= code <= last for first, last in KANJI_RANGES)


def _expand_iteration_marks(text: str) -> str:
    characters: list[str] = []
    for character in text:
        if (
            character == IDEOGRAPHIC_ITERATION_MARK
            and characters
            and _is_kanji(characters[-1])
        ):
            character = characters[-1]
        characters.append(character)
    return "".join(characters)


def fold_japanese_script(text: str) -> str:
    """Fold the script variants of one Japanese word to a single form."""
    text = unicodedata.normalize("NFC", text)
    text = _TRAILING_PROLONGED_MARK.sub("", text)
    text = _expand_iteration_marks(text)
    text = _COUNTER.sub(COUNTER_KA, text)
    return text.translate(_KATAKANA_TO_HIRAGANA)
