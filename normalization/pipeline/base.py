import re
from dataclasses import dataclass, field

from normalization.constants.protectors import PLACEHOLDER_FALLBACK_CHARS
from normalization.languages.base import LanguageOperators
from normalization.steps.base import TextStep, WordStep


@dataclass
class NormalizationPipeline:
    """
    Ordered, composable normalization pipeline.

    Structure mirrors the proven 3-stage approach, but each stage
    is now an explicit, inspectable list of steps.
    """

    name: str
    operators: LanguageOperators

    # Stage 1: full-text preprocessing
    text_pre_steps: list[TextStep] = field(default_factory=list)

    # Stage 2: per-word processing
    word_steps: list[WordStep] = field(default_factory=list)

    # Stage 3: full-text postprocessing
    text_post_steps: list[TextStep] = field(default_factory=list)

    def normalize(self, text: str) -> str:
        # Normalize whitespace
        text = re.sub(r"\s+", " ", text).strip()

        # Stage 1
        for step in self.text_pre_steps:
            text = step(text, self.operators)

        # Stage 2
        words = text.split(" ")
        words = [
            self._apply_word_steps(w)
            for w in words
            if w  # drop empty tokens
        ]
        text = " ".join(words)

        # Stage 3
        for step in self.text_post_steps:
            text = step(text, self.operators)

        # Restore any placeholders that dedicated steps left behind
        for placeholder, char in PLACEHOLDER_FALLBACK_CHARS.items():
            text = re.sub(
                rf"\s*{re.escape(placeholder)}\s*",
                char,
                text,
                flags=re.IGNORECASE,
            )

        return re.sub(r"\s+", " ", text).strip()

    def _apply_word_steps(self, word: str) -> str:
        for step in self.word_steps:
            word = step(word, self.operators)
        return word

    def validate(self) -> None:
        """
        Enforce pipeline structural constraints.

        Validates placeholder protect/restore pairing: every protect step in
        text_pre_steps must have its matching restore step(s) in text_post_steps.
        Updated in tandem with steps/text/placeholders.py.
        """
        # Maps each protect step name to the set of restore step names it requires.
        # Updated when protect/restore pairs are added to steps/text/placeholders.py.
        _PROTECT_REQUIRES: dict[str, set[str]] = {
            "protect_email_symbols": {
                "restore_email_at_symbol_with_word",
                "restore_email_dot_symbol_with_word",
            },
            "protect_phone_plus_symbol": {"restore_phone_plus_symbol"},
            "protect_time_colon": {"restore_time_colon"},
            "protect_unit_decimal": {"restore_unit_decimal_as_word"},
            "protect_unit_slash": {"restore_unit_slash"},
            "protect_number_separator_commas": {"remove_number_separator_markers"},
            "protect_decimal_separator": {"restore_decimal_separator_with_word"},
            "protect_hyphenated_letter_spelling": {"remove_letter_spelling_markers"},
            "protect_space_separated_letter_spelling": {
                "remove_letter_spelling_markers"
            },
        }

        pre_step_names = {s.name for s in self.text_pre_steps}
        post_step_names = {s.name for s in self.text_post_steps}

        errors: list[str] = []
        for protect_name, required_restores in _PROTECT_REQUIRES.items():
            if protect_name in pre_step_names:
                missing = required_restores - post_step_names
                if missing:
                    errors.append(
                        f"'{protect_name}' requires restore step(s) in text_post: {sorted(missing)}"
                    )

        if errors:
            raise ValueError(
                f"Pipeline '{self.name}' failed validation:\n"
                + "\n".join(f"  - {e}" for e in errors)
            )

    def describe(self) -> dict:
        """Introspect the pipeline — useful for debugging and docs."""
        return {
            "name": self.name,
            "language": self.operators.config.code,
            "text_pre_steps": [s.name for s in self.text_pre_steps],
            "word_steps": [s.name for s in self.word_steps],
            "text_post_steps": [s.name for s in self.text_post_steps],
        }
