from dataclasses import dataclass, field
from typing import TypeAlias

# Semantic type aliases for LanguageConfig dict fields.
# All are dict[str, str] structurally, but named to convey intent and
# make the config contract self-documenting for new language contributors.

TimeWords: TypeAlias = dict[str, str]
"""Maps spoken time values to digit strings.
Covers clock hours (1-12) and minute-worth values (13-50).
Example: {'one': '1', ..., 'twelve': '12', 'thirteen': '13', ..., 'fifty': '50'}

Compound minute expressions (e.g. 'twenty-one') are language-specific behavior
and are NOT stored here — see LanguageOperators.get_compound_minutes().
"""

SentenceReplacements: TypeAlias = dict[str, str]
"""Maps multi-word phrases to their normalized replacements.
Applied longest-match first. Example: {'good bye': 'goodbye'}
"""

DigitWords: TypeAlias = dict[str, str]
"""Maps word forms of single digits (0-9) to their digit characters.
Include both canonical forms and common spoken aliases.
Example (English): {'zero': '0', 'oh': '0', 'o': '0', 'one': '1', ..., 'nine': '9'}
"""

CurrencySymbols: TypeAlias = dict[str, str]
"""Maps currency symbols to their corresponding words."""


@dataclass
class LanguageConfig:
    code: str
    """ISO language code (e.g. 'en', 'fr') or 'default' for the language-neutral fallback."""
    decimal_separator: str = "."
    """Decimal separator character."""
    thousand_separator: str = ","
    """Thousands separator character."""
    decimal_word: str | None = None
    """Word used for decimal separator (e.g. 'point' in English, 'virgule' in French).
    None = decimal-word steps are skipped."""
    symbols_to_words: dict[str, str] = field(default_factory=dict)
    """Maps symbols to their corresponding words. Example: {'@': 'at', '.': 'dot', '+': 'plus'}"""
    currency_symbol_to_word: CurrencySymbols = field(default_factory=dict)
    """Maps currency symbols to their corresponding words. Example: {'€': 'euros', '$': 'dollars', '£': 'pounds', '¢': 'cents', '¥': 'yens'}"""
    filler_words: list[str] = field(default_factory=list)
    """Words to ignore during parsing."""
    oclock_word: str | None = None
    """The word or phrase meaning 'o'clock' in this language (e.g. "o'clock" for English).
    Used by convert_oclock_to_numeric_time. None = step is skipped."""
    time_words: TimeWords | None = None
    """Maps spoken time values to digit strings (hours 1-12 and minute values 13-50).
    Used by time normalization steps (o'clock patterns and word-based time patterns).
    Compound minute forms like 'twenty-one' are NOT included here — define them
    in LanguageOperators.get_compound_minutes() instead.
    None = time word steps are skipped."""
    sentence_replacements: SentenceReplacements | None = None
    """Multi-word phrase replacements applied before word splitting.
    Applied longest-match first. Used by apply_sentence_level_replacements. None = step is skipped."""
    digit_words: DigitWords | None = None
    """Maps word forms of single digits (0-9) to their digit characters.
    Used by steps that recognize isolated digit words in sequences or
    adjacent to special tokens (e.g. 'dot' in IP addresses / versions).
    Example (English): {'zero': '0', 'oh': '0', 'o': '0', 'one': '1', ..., 'nine': '9'}
    None = steps requiring digit word recognition are skipped."""
    number_words: list[str] | None = None
    """All number-related words for this language (digits, teens, tens, multipliers).
    Used by steps that need to identify number words in context (e.g. punctuation normalization).
    Example (English): ["zero", "oh", "o", "one", ..., "hundred", "thousand", "million"]
    None = steps requiring number word recognition are skipped."""
    plus_word: str | None = None
    """The word for 'plus' in this language (e.g. "plus" for English).
    Used by protect_plus_word_before_digit_words. None = step is skipped."""
    ordinal_suffixes: list[str] | None = None
    """Ordinal number suffixes for this language (e.g. ["st", "nd", "rd", "th"] for English).
    Used by steps that need to detect ordinal numbers. None = ordinal detection is skipped."""
    roman_numerals_uppercase_only: bool = False
    """When True, only treat Roman numerals as digits if they appear in ALL CAPS (e.g. VI, VIII).

    Avoids collisions with Nordic pronouns spelled ``vi``/``Vi``. Default False preserves
    legacy case-insensitive matching for other languages."""
    expand_all_caps_letter_by_letter: bool = True
    """When False, pure letter ALL-CAPS tokens (e.g. SMS) are not spaced into letters.

    Nordic STT hypotheses often keep acronyms as one word; default True preserves
    English-style letter-by-letter expansion for CAPS-only tokens."""
    am_word: str | None = None
    """Canonical AM time designator (e.g. "am" for English).
    Used by am/pm time formatting steps. None = am/pm steps are skipped."""
    pm_word: str | None = None
    """Canonical PM time designator (e.g. "pm" for English).
    Used by am/pm time formatting steps. None = am/pm steps are skipped."""
