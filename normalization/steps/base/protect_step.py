import re
from abc import abstractmethod

from normalization.constants.protectors import ProtectPlaceholder
from normalization.languages.base import LanguageOperators
from normalization.steps.base.text_step import TextStep


class ProtectStep(TextStep):
    """
    Protect characters with a placeholder.
    How to implement :
    - Define a class that inherits from ProtectStep.
    - Define the placeholder attribute to the ProtectPlaceholder enum value that corresponds to the characters to protect.
    - Implement the _pattern method to return a regular expression pattern that matches the characters to protect.
    """

    placeholder: ProtectPlaceholder

    @abstractmethod
    def _pattern(self, operators: LanguageOperators) -> re.Pattern: ...

    def __call__(self, text: str, operators: LanguageOperators) -> str:
        return self._pattern(operators).sub(rf"\1{self.placeholder.value}\2", text)
