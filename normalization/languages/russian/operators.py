from normalization.languages.base import LanguageConfig, LanguageOperators
from normalization.languages.registry import register_language
from normalization.languages.russian.number_normalizer import RussianNumberNormalizer
from normalization.languages.russian.replacements import RUSSIAN_REPLACEMENTS

# Russian writes the decimal separator as a comma (6,5) and groups thousands
# with a space (1 000 000), as in the examples of ГОСТ 8.417. No decimal word:
# a decimal is kept as "6,5", whichever separator it was written with.
RUSSIAN_CONFIG = LanguageConfig(
    code="ru",
    decimal_separator=",",
    thousand_separator=" ",
    symbols_to_words={
        "@": "собака",  # the usual Russian name of "@"
        ".": "точка",
        "+": "плюс",
        "=": "равно",
        ">": "больше",
        "<": "меньше",
        # The genitive plural, the form "%" is read with after most numbers
        # (5 процентов); the number normalizer folds the other forms to it.
        "%": "процентов",
    },
    # Hesitation sounds of spontaneous Russian speech. "ну" and "а" are words
    # (particles and conjunctions) and are never removed.
    filler_words=[
        "э",
        "ээ",
        "эээ",
        "эм",
        "мм",
        "ммм",
        "м м",  # "м-м" once remove_symbols has turned its hyphen into a space
        "хм",
        "гм",
    ],
)


@register_language
class RussianOperators(LanguageOperators):
    def __init__(self) -> None:
        super().__init__(RUSSIAN_CONFIG)
        self._number_normalizer = RussianNumberNormalizer()

    def expand_written_numbers(self, text: str) -> str:
        """Read Russian spelled-out numbers (двадцать пять -> 25) and fold the
        unit, year, percent and era words that follow a number."""
        return self._number_normalizer(text)

    def get_word_replacements(self) -> dict[str, str]:
        return RUSSIAN_REPLACEMENTS
