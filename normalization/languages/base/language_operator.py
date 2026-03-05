from normalization.languages.base.language_config import LanguageConfig
from normalization.languages.registery import register_language

DEFAULT_CONFIG = LanguageConfig(
    code="default",
    decimal_separator=".",
    decimal_word="point",
    dot_word="dot",
    thousand_separator=",",
    euro_word="euros",
    dollar_word="dollars",
    pound_word="pounds",
    cent_word="cents",
    yen_word="yen",
    at_word="at",
    percent_words=["percent"],
    greater_than_word="greater than",
    less_than_word="less than",
    equals_word="equals",
    degree_celsius_word="degree celsius",
    degree_fahrenheit_word="degree fahrenheit",
    filler_words=[],
    am_word="am",
    pm_word="pm",
)


@register_language
class LanguageOperators:
    """
    Behavioral contract: all language-specific text transformations.

    Adding a new language = subclassing this and implementing the relevant methods.
    Each method is intentionally fine-grained so contributors can override
    only what they need. Default implementations are all no-ops.

    Used directly (with no subclass) as the language-agnostic fallback when no
    language is specified or the language is unsupported. Must never crash.

    Number-related *data* (digit_words, number_words) lives in LanguageConfig.
    Override expand_written_numbers when the expansion *algorithm* differs.
    """

    def __init__(self, config: LanguageConfig = DEFAULT_CONFIG):
        self.config = config

    def expand_contractions(self, text: str) -> str:
        """Expand contractions (e.g. it's -> it is). No-op by default."""
        return text

    def normalize_numeric_time_formats(self, text: str) -> str:
        """Normalize numeric time formats (e.g. 05:45pm -> 5:45 pm). No-op by default."""
        return text

    def fix_one_word_in_numeric_contexts(self, text: str) -> str:
        """
        Convert the language word for 'one' to its digit when adjacent to other digits.

        Example (English): '10 one one' -> '10 1 1', 'one 5' -> '1 5'
        No-op by default.
        """
        return text

    def get_word_replacements(self) -> dict[str, str]:
        """Return the word-level replacement dict for this language. Empty by default."""
        return {}

    def get_compound_minutes(self) -> dict[str, str]:
        """Build compound minute expressions for this language (e.g. 'twenty-one' → '21').

        Called by word-based time pattern steps to match spoken compound minute values
        such as 'two twenty-one p.m' → '2:21 pm'.

        Compound minute formation is language-specific: English uses 'twenty-one' /
        'twenty one', but other languages may form these differently (or not at all).
        Return an empty dict if the language does not use compound minute expressions.
        """
        return {}

    def expand_written_numbers(self, text: str) -> str:
        """
        Expand written-out number expressions to digit form.

        Example: "twenty three" -> "23", "fifty" -> "50", "one hundred" -> "100"
        Return the text unchanged if not applicable for this language.
        """
        return text
