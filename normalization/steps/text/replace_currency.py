import re

from normalization.constants import ProtectPlaceholder
from normalization.languages.base import LanguageOperators
from normalization.steps.base import TextStep
from normalization.steps.registery import register_step

_CURRENCY_NUM = rf"\d+(?:{ProtectPlaceholder.DECIMAL_SEPARATOR.value}\d+)?"

RE_EURO_BEFORE = re.compile(rf"€\s*({_CURRENCY_NUM})", re.IGNORECASE)
RE_EURO_AFTER = re.compile(rf"({_CURRENCY_NUM})\s*€", re.IGNORECASE)
RE_DOLLAR_BEFORE = re.compile(rf"\$\s*({_CURRENCY_NUM})", re.IGNORECASE)
RE_DOLLAR_AFTER = re.compile(rf"({_CURRENCY_NUM})\s*\$", re.IGNORECASE)
RE_POUND_BEFORE = re.compile(rf"£\s*({_CURRENCY_NUM})", re.IGNORECASE)
RE_POUND_AFTER = re.compile(rf"({_CURRENCY_NUM})\s*£", re.IGNORECASE)
RE_CENT_BEFORE = re.compile(r"¢\s*(\d+)", re.IGNORECASE)
RE_CENT_AFTER = re.compile(r"(\d+)\s*¢", re.IGNORECASE)
RE_YEN_BEFORE = re.compile(r"¥\s*(\d+)", re.IGNORECASE)
RE_YEN_AFTER = re.compile(r"(\d+)\s*¥", re.IGNORECASE)


@register_step
class ReplaceCurrencyStep(TextStep):
    """
    Replace currency symbols with their corresponding words.

    Args:
        text: Input text

    Returns:
        Text with currency symbols replaced with their corresponding words
    """

    name = "replace_currency"

    def __call__(self, text: str, operators: LanguageOperators) -> str:
        cfg = operators.config
        # Symbol before/after number → "number word" (language from config)
        text = RE_EURO_BEFORE.sub(rf"\1 {cfg.euro_word}", text)
        text = RE_EURO_AFTER.sub(rf"\1 {cfg.euro_word}", text)
        text = RE_DOLLAR_BEFORE.sub(rf"\1 {cfg.dollar_word}", text)
        text = RE_DOLLAR_AFTER.sub(rf"\1 {cfg.dollar_word}", text)
        text = RE_POUND_BEFORE.sub(rf"\1 {cfg.pound_word}", text)
        text = RE_POUND_AFTER.sub(rf"\1 {cfg.pound_word}", text)
        text = RE_CENT_BEFORE.sub(rf"\1 {cfg.cent_word}", text)
        text = RE_CENT_AFTER.sub(rf"\1 {cfg.cent_word}", text)
        text = RE_YEN_BEFORE.sub(rf"\1 {cfg.yen_word}", text)
        text = RE_YEN_AFTER.sub(rf"\1 {cfg.yen_word}", text)
        return text
