from normalization.languages.base import LanguageConfig, LanguageOperators
from normalization.languages.registery import register_language

DEFAULT_CONFIG = LanguageConfig(
    code="default",
    decimal_separator=".",
    decimal_word="point",
    thousand_separator=",",
    symbols_to_words={
        "@": "at",
        ".": "dot",
        "+": "plus",
        "=": "equals",
        ">": "greater than",
        "<": "less than",
        "°": "degree",
        "°C": "degree celsius",
        "°F": "degree fahrenheit",
        "%": "percent",
    },
    currency_symbol_to_word={
        "€": "euros",
        "$": "dollars",
        "£": "pounds",
        "¢": "cents",
        "¥": "yen",
    },
    am_word="am",
    pm_word="pm",
)


@register_language
class DefaultOperators(LanguageOperators):
    """
    Language-agnostic fallback. All methods are no-ops inherited from
    LanguageOperators. Used when no language is specified or the language
    is unsupported. Must never crash.
    Default config:
    - code: "default"
    - decimal_separator: "."
    - decimal_word: "point"
    - dot_word: "dot"
    - thousand_separator: ","
    - symbols_to_words: {"@": "at", ".": "dot", "+": "plus", "=": "equals", ">": "greater than", "<": "less than", "°": "degree", "°C": "degree celsius", "°F": "degree fahrenheit", "%": "percent"}
    - currency_symbol_to_word: {"€": "euros", "$": "dollars", "£": "pounds", "¢": "cents", "¥": "yen"}
    - filler_words: []
    All methods are no-ops inherited from LanguageOperators.
    """

    def __init__(self):
        super().__init__(DEFAULT_CONFIG)
