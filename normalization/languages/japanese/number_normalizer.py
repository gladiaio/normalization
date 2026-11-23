"""Japanese number normalizer: kanji numerals to digits.

Horizontal Japanese writes numbers in Arabic digits, vertical Japanese in kanji
(公用文作成の考え方, 文化審議会, 2022, I-4 ア and キ), so a reference and a
transcript often write the same number two ways: 二十五メートル / 25メートル.
``words2num2`` reads kanji numerals inside running text; this module adds what
it leaves out and keeps what must not be read:

- Words built with a numeral, idioms and set phrases keep their kanji (same
  guidance, I-4 カ: 二者択一, 三日坊主, 四十九日, 七五三...). ``words2num2``
  already leaves most of them (一緒, 統一, 十分, 一般); ``_KEPT_AS_WRITTEN``
  lists the ones it would change, masked before it runs.
- Approximate numbers keep their kanji (I-4 オ: 数十人), so 数十 is not "数10".
- Counting with the native reading has two accepted forms, 一つ / 1つ and
  一人 / 1人 (I-4 カ (イ) and its note); ``words2num2`` reads 二つ but not 一つ.
- Digits mixed with the units 兆 億 万 千 百 十 (1万2千, 30万) are read as one
  number, as are positional kanji digits with 〇 (二〇二五年) and a kanji
  decimal written with 中黒 (一・五).
"""

from __future__ import annotations

import re

from words2num2 import words2num_sentence

_LANGUAGE = "ja"

# Words that hold a numeral but are not a number (idioms, set phrases, lexicalised
# compounds), and that words2num2 would read as one. The guidance examples come
# from 公用文作成の考え方 I-4 カ; the others are dictionary words (JMdict).
_KEPT_AS_WRITTEN: tuple[str, ...] = (
    # 公用文作成の考え方 I-4 カ (ア) (ウ) (エ)
    "千里の道も一歩から",
    "三日坊主",
    "再三再四",
    "二者択一",
    "三権分立",
    "六法全書",
    "七福神",
    "二十四節気",
    "七五三",
    "四十九日",
    "前九年の役",
    "三国干渉",
    "お七夜",
    # Dictionary words
    "一部",  # いちぶ, "a part"
    "一層",  # いっそう, "all the more"
    "一番",  # いちばん, "most"; 一番目 is an ordinal and is read
    "万一",  # まんいち, "in case"
    "万が一",
    "三日月",  # みかづき, "crescent moon"
    "八百屋",  # やおや, "greengrocer"
    "十八番",  # おはこ, "one's specialty"
    "五分五分",  # ごぶごぶ, "even"
    "五月雨",  # さみだれ, "early-summer rain"
    "八十八夜",
    "百人一首",
    "八つ当たり",
    "十人十色",
    "万歳",  # ばんざい
    "万年筆",  # まんねんひつ, "fountain pen"
    "三角",  # さんかく, "triangle"
)

# A kept word is still read when it is clearly a number: an ordinal (第一部,
# 一番目) or a word glued to a preceding numeral.
_NUMERAL_CHARACTERS = "0-9０-９〇一二三四五六七八九十百千万億兆"
_KEPT_PATTERN = re.compile(
    rf"(?<![第{_NUMERAL_CHARACTERS}])(?:"
    + "|".join(re.escape(w) for w in sorted(_KEPT_AS_WRITTEN, key=lambda w: -len(w)))
    + r")(?!目)"
)

# Approximate numbers (I-4 オ): 数十人, 何百回. Kept as written.
_APPROXIMATE_PATTERN = re.compile(r"[数何幾][十百千万億]+")

# Accepted counting forms that words2num2 leaves in kanji (I-4 カ (イ) note:
# "１つ、２つ、３つ…" is widely used in horizontal writing).
_COUNTING_FORMS: dict[str, str] = {"一つ": "1つ"}

# Private-use characters stand for a masked span while words2num2 runs.
_MASK_BASE = 0xE000

_KANJI_DIGITS: dict[str, int] = {
    "〇": 0,
    "零": 0,
    "一": 1,
    "二": 2,
    "三": 3,
    "四": 4,
    "五": 5,
    "六": 6,
    "七": 7,
    "八": 8,
    "九": 9,
}
_SMALL_UNITS: dict[str, int] = {"十": 10, "百": 100, "千": 1_000}
_LARGE_UNITS: dict[str, int] = {
    "万": 10_000,
    "億": 100_000_000,
    "兆": 1_000_000_000_000,
}

# 二〇二五年, 一〇〇: kanji digits written by position; the 〇 tells them apart from
# a range such as 三四人 ("three or four").
_POSITIONAL_PATTERN = re.compile(
    r"(?<![十百千万億兆])[〇一二三四五六七八九]*〇[〇一二三四五六七八九]*(?![十百千万億兆])"
)
_POSITIONAL_MIN_LENGTH = 2

# 一・五 (1.5): a kanji decimal written with the middle dot.
_KANJI_DECIMAL_PATTERN = re.compile(
    r"([〇一二三四五六七八九十百千]+)・([〇一二三四五六七八九]+)"
)

# Digits mixed with kanji units: 1万2千, 30万, 1億2644万3000, 1万二千. Not glued to an
# ASCII letter, digit or "." on the left, so a protected decimal (1XDECIMALX5万)
# or a code is left alone.
_MIXED_PATTERN = re.compile(
    r"(?<![0-9A-Za-z.０-９])[0-9０-９]+[十百千万億兆]"
    r"(?:[0-9０-９〇一二三四五六七八九]*[十百千万億兆])*[0-9０-９〇一二三四五六七八九]*"
)


def _parse_units(text: str) -> int:
    """Value of digits and kanji units in order (1万2千 → 12000)."""
    total = 0
    section = 0
    current: int | None = None
    for token in re.findall(r"[0-9０-９]+|.", text):
        if token in _KANJI_DIGITS:
            current = _KANJI_DIGITS[token]
        elif token in _SMALL_UNITS:
            section += (1 if current is None else current) * _SMALL_UNITS[token]
            current = None
        elif token in _LARGE_UNITS:
            section += 0 if current is None else current
            total += (section or 1) * _LARGE_UNITS[token]
            section = 0
            current = None
        else:
            current = int(token)
    return total + section + (current or 0)


def _read_positional(match: re.Match[str]) -> str:
    digits = match.group(0)
    if len(digits) < _POSITIONAL_MIN_LENGTH:
        return digits
    return "".join(str(_KANJI_DIGITS[c]) for c in digits)


def _read_kanji_decimal(match: re.Match[str]) -> str:
    integer = _parse_units(match.group(1))
    fraction = "".join(str(_KANJI_DIGITS[c]) for c in match.group(2))
    return f"{integer}.{fraction}"


class JapaneseNumberNormalizer:
    """Read Japanese kanji numerals as digits, keeping idioms as written."""

    def __call__(self, text: str) -> str:
        if not text.strip():
            return text
        masked: list[str] = []

        def _mask(match: re.Match[str]) -> str:
            masked.append(match.group(0))
            return chr(_MASK_BASE + len(masked) - 1)

        text = _KEPT_PATTERN.sub(_mask, text)
        text = _APPROXIMATE_PATTERN.sub(_mask, text)
        for kanji, digits in _COUNTING_FORMS.items():
            text = text.replace(kanji, digits)
        text = _KANJI_DECIMAL_PATTERN.sub(_read_kanji_decimal, text)
        text = _POSITIONAL_PATTERN.sub(_read_positional, text)
        # Before words2num2, which misreads a digit glued to a unit (30万円).
        text = _MIXED_PATTERN.sub(lambda m: str(_parse_units(m.group(0))), text)
        text = words2num_sentence(text, lang=_LANGUAGE)
        for index, original in enumerate(masked):
            text = text.replace(chr(_MASK_BASE + index), original)
        return text
