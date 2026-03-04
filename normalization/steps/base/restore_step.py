from abc import abstractmethod

from normalization.constants.protectors import ProtectPlaceholder
from normalization.languages.base import LanguageOperators
from normalization.steps.base.text_step import TextStep


class RestoreStep(TextStep):
    """
    Restore the protected placeholder.
    """

    placeholder: ProtectPlaceholder

    @abstractmethod
    def _replacement(self, operators: LanguageOperators) -> str: ...

    def __call__(self, text: str, operators: LanguageOperators) -> str:
        text = text.replace(self.placeholder.value, self._replacement(operators))
        text = text.replace(
            self.placeholder.value.lower(), self._replacement(operators)
        )
        return text
