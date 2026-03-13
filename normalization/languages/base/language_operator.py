from normalization.languages.base.language_config import LanguageConfig

_DEFAULT_CONFIG = LanguageConfig(code="default")


class LanguageOperators:
    """
    Base language operator and language-neutral fallback.

    Directly instantiable: when no config is provided, uses a minimal
    language-neutral config (code="default") with empty symbol/currency
    mappings and all optional fields set to None.

    Adding a new language = subclassing this and implementing the relevant
    methods. Each method is intentionally fine-grained so contributors can
    override only what they need. Default implementations are all no-ops.

    Number-related *data* (digit_words, number_words) lives in LanguageConfig.
    Override expand_written_numbers when the expansion *algorithm* differs.
    """

    def __init__(self, config: LanguageConfig | None = None):
        self.config = config if config is not None else _DEFAULT_CONFIG

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
