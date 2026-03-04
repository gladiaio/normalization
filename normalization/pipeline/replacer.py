import logging
import re

logger = logging.getLogger(__name__)


class Replacer:
    """Stateful compiled-regex engine for word-level replacements.

    Pre-compiles one \\b-bounded pattern per mapping entry at init time.
    At least one side of each mapping pair must be a single word.
    """

    def __init__(self, mapping: dict[str, str]):
        patterns: dict[re.Pattern, str] = {}
        for left, right in mapping.items():
            left_is_single = len(left.strip().split()) == 1
            right_is_single = len(right.strip().split()) == 1

            if not left_is_single and not right_is_single:
                logger.warning(
                    f"At least one side must be a single word: '{left}' - '{right}'"
                )
                continue

            if left_is_single:
                bad, good = left, right
            else:
                bad, good = right, left

            patterns[re.compile(rf"\b{re.escape(bad)}\b")] = good

        self.patterns = patterns

    def __call__(self, text: str) -> str:
        for pattern, replacement in self.patterns.items():
            text = pattern.sub(replacement, text)
        return text
