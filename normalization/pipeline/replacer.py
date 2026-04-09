import logging
import re

logger = logging.getLogger(__name__)


class Replacer:
    """Stateful word-replacement engine.

    Single-word keys are stored in a plain dict for O(1) lookup.
    Multi-word keys (where the right side is a single word) fall back to
    pre-compiled \\b-bounded regex patterns.

    At least one side of each mapping pair must be a single word.
    """

    def __init__(self, mapping: dict[str, str]):
        # Fast path: single-word key → direct dict lookup
        self._word_map: dict[str, str] = {}
        # Fallback: multi-word key (right side must be single word)
        self._multi_patterns: list[tuple[re.Pattern[str], str]] = []

        for left, right in mapping.items():
            left_is_single = len(left.strip().split()) == 1
            right_is_single = len(right.strip().split()) == 1

            if not left_is_single and not right_is_single:
                logger.warning(
                    f"At least one side must be a single word: '{left}' - '{right}'"
                )
                continue

            if left_is_single:
                self._word_map[left.strip()] = right
            else:
                # right is single word, left is multi-word: match multi-word phrase
                self._multi_patterns.append(
                    (re.compile(rf"\b{re.escape(left.strip())}\b"), right)
                )

        # Keep a public alias for backwards compatibility
        self.patterns = {
            re.compile(rf"\b{re.escape(k)}\b"): v for k, v in self._word_map.items()
        } | {p: r for p, r in self._multi_patterns}

    def __call__(self, text: str) -> str:
        # Fast path: single-word input (no spaces) → dict lookup
        if " " not in text.strip():
            return self._word_map.get(text.strip(), text)
        # Multi-word input: apply regex patterns
        for pattern, replacement in self._multi_patterns:
            text = pattern.sub(replacement, text)
        return text
