from normalization.languages.base import LanguageConfig, LanguageOperators
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
    - euro_word: "euros"
    - dollar_word: "dollars"
    - pound_word: "pounds"
    - cent_word: "cents"
    - at_word: "at"
    - percent_words: ["percent"]
    - greater_than_word: "greater than"
    - less_than_word: "less than"
    - equals_word: "equals"
    - degree_celsius_word: "degree celsius"
    - degree_fahrenheit_word: "degree fahrenheit"
    - filler_words: []
    All methods are no-ops inherited from LanguageOperators.
    """

    def __init__(self):
        super().__init__(DEFAULT_CONFIG)
