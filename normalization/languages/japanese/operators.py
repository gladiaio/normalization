from normalization.languages.base import LanguageConfig, LanguageOperators
from normalization.languages.japanese.number_normalizer import JapaneseNumberNormalizer
from normalization.languages.japanese.replacements import JAPANESE_REPLACEMENTS
from normalization.languages.registry import register_language

# Horizontal Japanese writes numbers with "." for decimals and "," every three
# digits (公用文作成の考え方, 2022, I-4 イ: "5,000  62,250円  1,254,372人").
JAPANESE_CONFIG = LanguageConfig(
    code="ja",
    decimal_separator=".",
    thousand_separator=",",
    # Katakana loanword readings, as in an e-mail address read aloud.
    symbols_to_words={
        "@": "アット",
        ".": "ドット",
        "+": "プラス",
    },
)


@register_language
class JapaneseOperators(LanguageOperators):
    def __init__(self) -> None:
        super().__init__(JAPANESE_CONFIG)
        self._number_normalizer = JapaneseNumberNormalizer()

    def expand_written_numbers(self, text: str) -> str:
        """Read kanji numerals as digits (二十五メートル → 25メートル, 1万2千 → 12000)."""
        return self._number_normalizer(text)

    def get_word_replacements(self) -> dict[str, str]:
        return JAPANESE_REPLACEMENTS
