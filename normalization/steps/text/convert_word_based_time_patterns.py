import re
from typing import NamedTuple

from normalization.languages.base import LanguageOperators
from normalization.steps.base import TextStep
from normalization.steps.registry import register_step


def _ampm_prefix_class(am_word: str, pm_word: str) -> str:
    """Build a regex character class from the first characters of am/pm words."""
    return f"[{re.escape(am_word[0])}{re.escape(pm_word[0])}]"


class _CompiledPatterns(NamedTuple):
    # List of (compiled_pattern, replacement) for hour+compound_minute+ampm
    compound_minute: list[tuple[re.Pattern[str], str]]
    # List of (compiled_pattern, replacement) for hour+minute_word+ampm
    minute_word: list[tuple[re.Pattern[str], str]]
    # List of (compiled_pattern, replacement) for hour+ampm only
    hour_only: list[tuple[re.Pattern[str], str]]
    # (compiled_pattern, replacement) for digit+oclock, or None
    oclock: tuple[re.Pattern[str], str] | None
    # (compiled_pattern, replacement) for digit:00+ampm collapse, or None
    oclock_ampm: tuple[re.Pattern[str], str] | None


def _build_compiled_patterns(operators: LanguageOperators) -> _CompiledPatterns:
    time_words = operators.config.time_words
    am_word = operators.config.am_word
    pm_word = operators.config.pm_word
    oclock_word = operators.config.oclock_word

    compound_minute: list[tuple[re.Pattern[str], str]] = []
    minute_word: list[tuple[re.Pattern[str], str]] = []
    hour_only: list[tuple[re.Pattern[str], str]] = []
    oclock: tuple[re.Pattern[str], str] | None = None
    oclock_ampm: tuple[re.Pattern[str], str] | None = None

    if time_words is not None and am_word is not None and pm_word is not None:
        compound = operators.get_compound_minutes()
        prefix_class = _ampm_prefix_class(am_word, pm_word)

        for hour_word, hour_num in time_words.items():
            for min_pattern, min_num in compound.items():
                compound_minute.append(
                    (
                        re.compile(
                            rf"\b{hour_word}\s+{min_pattern}\s+({prefix_class})\.?m\.?\b",
                            re.IGNORECASE,
                        ),
                        rf"{hour_num}:{min_num} \1m",
                    )
                )

        for hour_word, hour_num in time_words.items():
            for min_word, min_num in time_words.items():
                minute_word.append(
                    (
                        re.compile(
                            rf"\b{hour_word}\s+{min_word}\s+({prefix_class})\.?m\.?\b",
                            re.IGNORECASE,
                        ),
                        rf"{hour_num}:{min_num} \1m",
                    )
                )

        for word, num in time_words.items():
            hour_only.append(
                (
                    re.compile(
                        rf"\b{word}\s+({prefix_class})\.?m\.?\b",
                        re.IGNORECASE,
                    ),
                    rf"{num} \1m",
                )
            )

    if oclock_word is not None:
        escaped = re.escape(oclock_word)
        oclock = (
            re.compile(rf"(\d{{1,2}})\s+{escaped}", re.IGNORECASE),
            r"\1:00",
        )
        if am_word is not None and pm_word is not None:
            prefix_class = _ampm_prefix_class(am_word, pm_word)
            oclock_ampm = (
                re.compile(rf"(\d{{1,2}}):00\s+({prefix_class}m)"),
                r"\1 \2",
            )

    return _CompiledPatterns(
        compound_minute, minute_word, hour_only, oclock, oclock_ampm
    )


@register_step
class ConvertWordBasedTimePatternsStep(TextStep):
    """Convert word-based time patterns (two p.m -> 2 pm, two thirty p.m -> 2:30 pm).

    Reads operators.config.time_words, operators.config.am_word,
    operators.config.pm_word, operators.config.oclock_word, and
    operators.get_compound_minutes().
    No-op when required config is None.

    Regex patterns are compiled once per operators config instance and cached
    on the step to avoid recompilation on every call.
    """

    name = "convert_word_based_time_patterns"

    def __init__(self) -> None:
        self._cache: dict[int, _CompiledPatterns] = {}

    def _get_patterns(self, operators: LanguageOperators) -> _CompiledPatterns:
        key = id(operators.config)
        if key not in self._cache:
            self._cache[key] = _build_compiled_patterns(operators)
        return self._cache[key]

    def __call__(self, text: str, operators: LanguageOperators) -> str:
        patterns = self._get_patterns(operators)

        for compiled, repl in patterns.compound_minute:
            text = compiled.sub(repl, text)

        for compiled, repl in patterns.minute_word:
            text = compiled.sub(repl, text)

        for compiled, repl in patterns.hour_only:
            text = compiled.sub(repl, text)

        if patterns.oclock is not None:
            compiled, repl = patterns.oclock
            text = compiled.sub(repl, text)

        if patterns.oclock_ampm is not None:
            compiled, repl = patterns.oclock_ampm
            text = compiled.sub(repl, text)

        return text
