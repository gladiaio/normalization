import re

from normalization.languages.base import LanguageOperators
from normalization.steps.base import TextStep
from normalization.steps.registry import register_step

_RE_DOMAIN_3PARTS = re.compile(r"\b([a-zA-Z]+)\.([a-zA-Z]+)\.([a-zA-Z]+)(\d*)\b")
_RE_DOMAIN_2PARTS = re.compile(r"\b([a-zA-Z]+)\.([a-zA-Z]{2,})\b")
_RE_IP_ADDRESS = re.compile(r"\b(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})\b")
_RE_VERSION_V_PREFIX = re.compile(r"\b(v)(\d+)\.(\d+)\.(\d+)\b")
_RE_VERSION_3PARTS = re.compile(r"\b(\d+)\.(\d+)\.(\d+)\b")
_RE_VERSION_V_SUFFIX = re.compile(r"\b([a-z]+)\.([a-z]+)\.v(\d+)\b")
_RE_FILE_EXTENSION = re.compile(r"\b([a-zA-Z0-9_\-]+)\.([a-zA-Z]{2,4})\b")


@register_step
class ConvertDotsToWordsInTechnicalContextsStep(TextStep):
    """Convert dots in domains, IPs, versions, file extensions to the language dot word, defined in language config in operator."""

    name = "convert_dots_to_words_in_technical_contexts"

    def __call__(self, text: str, operators: LanguageOperators) -> str:
        dot = operators.config.symbols_to_words.get(".")
        if dot is None:
            return text
        text = _RE_DOMAIN_3PARTS.sub(rf"\1 {dot} \2 {dot} \3\4", text)
        text = _RE_DOMAIN_2PARTS.sub(rf"\1 {dot} \2", text)
        text = _RE_IP_ADDRESS.sub(rf"\1 {dot} \2 {dot} \3 {dot} \4", text)
        text = _RE_VERSION_V_PREFIX.sub(rf"\1\2 {dot} \3 {dot} \4", text)
        text = _RE_VERSION_3PARTS.sub(rf"\1 {dot} \2 {dot} \3", text)
        text = _RE_VERSION_V_SUFFIX.sub(rf"\1 {dot} \2 {dot} v\3", text)
        text = _RE_FILE_EXTENSION.sub(rf"\1 {dot} \2", text)
        return text
