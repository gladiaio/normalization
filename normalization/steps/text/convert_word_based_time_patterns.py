import re

from normalization.languages.base import LanguageOperators
from normalization.steps.base import TextStep
from normalization.steps.registry import register_step


def _ampm_prefix_class(am_word: str, pm_word: str) -> str:
    """Build a regex character class from the first characters of am/pm words."""
    return f"[{re.escape(am_word[0])}{re.escape(pm_word[0])}]"


@register_step
class ConvertWordBasedTimePatternsStep(TextStep):
    """Convert word-based time patterns (two p.m -> 2 pm, two thirty p.m -> 2:30 pm).

    Reads operators.config.time_words, operators.config.am_word,
    operators.config.pm_word, operators.config.oclock_word, and
    operators.get_compound_minutes().
    No-op when required config is None.
    """

    name = "convert_word_based_time_patterns"

    def __call__(self, text: str, operators: LanguageOperators) -> str:
        time_words = operators.config.time_words
        am_word = operators.config.am_word
        pm_word = operators.config.pm_word
        oclock_word = operators.config.oclock_word

        if time_words is not None and am_word is not None and pm_word is not None:
            compound = operators.get_compound_minutes()
            prefix_class = _ampm_prefix_class(am_word, pm_word)

            for hour_word, hour_num in time_words.items():
                for min_pattern, min_num in compound.items():
                    text = re.sub(
                        rf"\b{hour_word}\s+{min_pattern}\s+({prefix_class})\.?m\.?\b",
                        rf"{hour_num}:{min_num} \1m",
                        text,
                        flags=re.IGNORECASE,
                    )

            for hour_word, hour_num in time_words.items():
                for min_word, min_num in time_words.items():
                    text = re.sub(
                        rf"\b{hour_word}\s+{min_word}\s+({prefix_class})\.?m\.?\b",
                        rf"{hour_num}:{min_num} \1m",
                        text,
                        flags=re.IGNORECASE,
                    )

            for word, num in time_words.items():
                text = re.sub(
                    rf"\b{word}\s+({prefix_class})\.?m\.?\b",
                    rf"{num} \1m",
                    text,
                    flags=re.IGNORECASE,
                )

        if oclock_word is not None:
            escaped = re.escape(oclock_word)
            text = re.sub(
                rf"(\d{{1,2}})\s+{escaped}", r"\1:00", text, flags=re.IGNORECASE
            )
            if am_word is not None and pm_word is not None:
                prefix_class = _ampm_prefix_class(am_word, pm_word)
                text = re.sub(rf"(\d{{1,2}}):00\s+({prefix_class}m)", r"\1 \2", text)

        return text
