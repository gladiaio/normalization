# Step Reference

Auto-generated — do not edit by hand. Run `scripts/generate_step_docs.py` to update.

## Text Steps

### `apply_sentence_level_replacements`

**Base class:** `TextStep`

Apply multi-word phrase replacements (e.g. 'good bye' -> 'goodbye').

Reads operators.config.sentence_replacements. Applies longest match first so that more specific phrases take priority over shorter overlapping ones.
No effect when the dict is empty.

### `casefold_text`

**Base class:** `TextStep`

Lowercase all text using str.casefold().

### `convert_comparison_operators_to_words`

**Base class:** `TextStep`

Convert >, <, = to language-specific words in numeric contexts using language config from operators.

### `convert_decimal_periods_to_decimal_word`

**Base class:** `TextStep`

Convert remaining decimal periods to the language decimal word, defined in language config from operators.

'10.5' -> '10 point 5' (English).
Avoids patterns already converted to 'dot' (IPs, versions).

### `convert_degree_symbols_to_words`

**Base class:** `TextStep`

Convert °C and °F to language-specific words using language config from operators.

### `convert_digit_word_sequences_to_digits`

**Base class:** `TextStep`

Convert sequences of 3+ digit words to actual digits.

'two one three four' -> '2134', 'seven zero' stays (only 2 words).
Delegates the word-to-digit mapping to operators.config.digit_words.

### `convert_dots_to_words_in_technical_contexts`

**Base class:** `TextStep`

Convert dots in domains, IPs, versions, file extensions to the language dot word, defined in language config in operator.

### `convert_oclock_to_numeric_time`

**Base class:** `TextStep`

Convert 'ten o'clock' -> '10:00'.

Reads operators.config.oclock_word and operators.config.time_words.
Only entries whose digit value is 1-12 (valid clock hours) are used;
minute-range values (13-50) present in time_words are ignored here.
No-op when either field is None.

### `convert_roman_numerals_to_digits`

**Base class:** `TextStep`

Convert simple Roman numerals (II-IX) to Arabic digits in full text.

Runs before expand_alphanumeric_codes to prevent 'VIII' -> 'V I I I'.
Only converts ii-ix to avoid false positives with single letters like 'I'.
Skips 'v' when adjacent to digits (version-like contexts: v2, v 12).

### `convert_word_based_time_patterns`

**Base class:** `TextStep`

Convert word-based time patterns (two p.m -> 2 pm, two thirty p.m -> 2:30 pm).

Reads operators.config.time_words, operators.config.am_word,
operators.config.pm_word, operators.config.oclock_word, and
operators.get_compound_minutes().
No-op when required config is None.

### `expand_alphanumeric_codes`

**Base class:** `TextStep`

Space out uppercase words and alphanumeric codes.

'ABC123' -> 'A B C 1 2 3', 'CNN' -> 'C N N'.
Skips pure numbers, ordinals (1st, 2nd), and protection markers. Must run before casefold_text.

### `expand_contractions`

**Base class:** `TextStep`

Expand contractions (it's -> it is, can't -> cannot).

Delegates to operators.expand_contractions().

### `expand_written_numbers_to_digits`

**Base class:** `TextStep`

Convert written numbers to digits (fifty -> 50, twenty three -> 23). Delegates to operators.expand_written_numbers().

### `expand_www_abbreviation`

**Base class:** `TextStep`

Expand 'www' to 'W W W'.

### `fix_ampm_letter_spacing`

**Base class:** `TextStep`

Collapse 'a m' / 'p m' into 'am' / 'pm' after time digits.

Reads operators.config.am_word and operators.config.pm_word.
No-op when either is None.

### `fix_dot_adjacent_number_words`

**Base class:** `TextStep`

Convert number words back to digits when adjacent to 'dot' (IPs/versions).

'zero dot one dot two' -> '0 dot 1 dot 2'.
Single-character entries (e.g. 'o') are excluded to avoid false positives
in non-numeric contexts.

### `fix_one_word_in_numeric_contexts`

**Base class:** `TextStep`

Convert the word for 'one' to its digit when adjacent to other digits.

Example (English): '10 one one' -> '10 1 1', 'one 5' -> '1 5'

### `fix_version_number_v_prefix`

**Base class:** `TextStep`

Collapse space between 'v' and digit (v 2 -> v2). 'v' must be followed by a digit.

### `format_time_patterns_with_ampm`

**Base class:** `TextStep`

Format '5 45 p m' -> '5:45 pm' and '545 pm' -> '5:45 pm'.

Reads operators.config.am_word and operators.config.pm_word.
No-op when either is None.

### `normalize_numeric_time_formats`

**Base class:** `TextStep`

Normalize numeric time formats (05:45pm -> 5:45 pm, 5.45 p.m. -> 5:45 pm).

Delegates to operators.normalize_numeric_time_formats().

### `normalize_punctuation_between_number_words`

**Base class:** `TextStep`

Replace commas, dots, hyphens between number words with a single space.

Handles: 'seven, zero' -> 'seven zero', 'two-one-three' -> 'two one three'.
Reads operators.config.number_words. No-op when None.

### `normalize_whitespace`

**Base class:** `TextStep`

Collapse multiple spaces into one and strip leading/trailing whitespace.

### `protect_decimal_separator`

**Base class:** `ProtectStep`

Protect the decimal separator from being removed by RemoveSymbolsStep.

### `protect_email_symbols`

**Base class:** `TextStep`

Replace @ and . inside email addresses with placeholders.

A single email match requires protecting two different symbols (@ → EMAIL_AT, . → EMAIL_DOT) in one pass. ProtectStep handles exactly one placeholder per substitution.

### `protect_hyphenated_letter_spelling`

**Base class:** `TextStep`

Mark single-letter-hyphen sequences to prevent false conversions.

Uses TextStep directly: the replacement is a per-match function that splits on '-' and suffixes each individual letter. Example: "b-o-b" → "bxltrx oxltrx bxltrx".

### `protect_number_separator_commas`

**Base class:** `TextStep`

Replace comma/dot+space between digits with ¤ marker. (1, 2, 3 -> 1 ¤ 2 ¤ 3)

Two independent patterns (comma-separated and
dot-separated) both collapse to the same marker. ProtectStep handles a
single pattern mapping to a single placeholder.

### `protect_phone_plus_symbol`

**Base class:** `TextStep`

Replace "+" when it appears right before a digit (like in phone numbers) with a special placeholder.

The regex pattern "\+(?=\d)" means:
- Match a literal "+" character
- But only if it is immediately followed by a number (0-9)
- The digit is NOT included in the match (it stays untouched)

For example:
"+123456" → the "+" is replaced, but "123456" stays the same.

Note: The pattern uses a lookahead (?=\d), which checks what comes next
without capturing it as part of the match.

### `protect_plus_word_before_digit_words`

**Base class:** `TextStep`

Convert the plus word to XPLUSX before digit words (phone number context).

Reads operators.config.plus_word and operators.config.digit_words.
No-op when plus_word is None or digit_words is empty/None.

### `protect_space_separated_letter_spelling`

**Base class:** `TextStep`

Mark sequences of 3+ single letters to prevent false conversions.

Uses TextStep directly: same reason as ProtectHyphenatedLetterSpellingStep —
the replacement is a per-match function that suffixes each individual letter.

### `protect_time_colon`

**Base class:** `ProtectStep`

Protect the colon used in time expressions like HH:MM.
Matches times written with one or two digits for the hour and exactly two digits for the minutes (e.g., "9:30", "12:05").
The colon between them is temporarily replaced with a placeholder so it is not modified or removed by later text-processing steps.

Example:
"9:30" → "9§30"  (colon replaced with placeholder)

### `protect_unit_decimal`

**Base class:** `ProtectStep`

Replace . in decimal unit expressions with ‡ placeholder (e.g. 9.8 m/s → 9‡8 m/s).

### `protect_unit_slash`

**Base class:** `ProtectStep`

Replace / in unit expressions with † placeholder (e.g. km/h → km†h).

### `remove_acronym_periods`

**Base class:** `TextStep`

Remove periods from acronyms (U.S.A. -> USA, U.S. -> US).

### `remove_diacritics`

**Base class:** `TextStep`

Normalize text by removing diacritics and converting special accented letters to their ASCII equivalents. (é -> e, ê -> e, etc.)

### `remove_filler_words`

**Base class:** `TextStep`

Remove filler words defined in the language config (um, uh, euh, etc.).

### `remove_hash_before_numbers`

**Base class:** `TextStep`

Remove # symbol before numbers (#1 -> 1).

### `remove_letter_spelling_markers`

**Base class:** `TextStep`

Strip xltrx suffix markers from letters.

Uses TextStep directly: the suffix is a token-embedded string (not a
standalone token), so removal requires a regex word-boundary match.
Example: "bxltrx oxltrx bxltrx" → "b o b"

### `remove_non_numeric_trailing_dots`

**Base class:** `TextStep`

Remove dots that are not between digits (.X -> ' X', trailing .).

### `remove_number_separator_markers`

**Base class:** `TextStep`

Strip ¤ markers from the text.

Uses TextStep directly: the marker is deleted entirely (not restored to a
character or word). RestoreStep replaces with a non-empty string; here the
surrounding whitespace must also be collapsed to nothing.

### `remove_spaces_between_adjacent_digits`

**Base class:** `TextStep`

Collapse spaces between adjacent digits (1 2 3 -> 123).

Preserves spaces around 'point' (decimal word) and before ordinals.
Handles ¤ markers by processing segments separately.

### `remove_standalone_currency_symbols`

**Base class:** `TextStep`

Remove currency symbols that are not adjacent to numbers.

### `remove_symbols`

**Base class:** `TextStep`

Replace markers, symbols, and punctuation with spaces.

Preserves letters, digits, and all placeholder characters.

### `remove_thousand_separators`

**Base class:** `TextStep`

Remove thousand separators based on the language config.

English uses comma (1,234 -> 1234), European languages use period (1.234 -> 1234).

### `remove_trailing_apostrophe_space`

**Base class:** `TextStep`

Remove space before apostrophe (' s -> 's).

### `remove_trailing_dot_word_from_emails`

**Base class:** `TextStep`

Remove trailing 'dot' after email-like words at end of text.

### `remove_trailing_period`

**Base class:** `TextStep`

Remove trailing period from text.

### `remove_zero_minutes_from_time`

**Base class:** `TextStep`

Remove :00 from time expressions (10:00 pm -> 10 pm).

Reads operators.config.am_word and operators.config.pm_word.
No-op when either is None.

### `replace_currency`

**Base class:** `TextStep`

Replace currency symbols with their corresponding words.

### `restore_decimal_separator_with_word`

**Base class:** `RestoreStep`

Restore XDECIMALX placeholder with the language-specific decimal word.

### `restore_email_at_symbol_with_word`

**Base class:** `TextStep`

Restore XATX placeholder with the language-specific 'at' word.

Uses TextStep directly: ProtectEmailSymbolsStep inserts spaces around the
placeholder, so restoration uses re.sub with \s* to absorb them.
RestoreStep only does a plain str.replace, which would leave double spaces.

When no word is configured for '@', restores the original '@' character
so that placeholders never leak into the final output.

### `restore_email_dot_symbol_with_word`

**Base class:** `TextStep`

Restore XDOTX placeholder with the language-specific 'dot' word.

Uses TextStep directly: same reason as RestoreEmailAtSymbolWithWordStep — spaces were inserted around the placeholder during protection.

When no word is configured for '.', restores the original '.' character so that placeholders never leak into the final output.

### `restore_phone_plus_symbol`

**Base class:** `TextStep`

Restore XPLUSX placeholder back to + and collapse trailing space.

Beyond the plain replace, it must also collapse "+ <digit>" → "+<digit>" (e.g. after casefold splits the token). RestoreStep only does plain string replacement.

### `restore_time_colon`

**Base class:** `RestoreStep`

Restore § placeholder back to colon.

### `restore_unit_decimal_as_word`

**Base class:** `RestoreStep`

Restore ‡ placeholder with the language-specific decimal word.

### `restore_unit_slash`

**Base class:** `RestoreStep`

Restore † placeholder back to /.

## Word Steps

### `apply_word_replacements`

**Base class:** `WordStep`

Apply single-word replacements from the language operators.

Skips email tokens. Uses a cached Replacer keyed on the language code.
