from normalization.languages.norwegian.operators import NorwegianOperators
from normalization.steps.text.replace_currency import ReplaceCurrencyStep


def test_kr_not_matched_inside_kroner() -> None:
    ops = NorwegianOperators()
    step = ReplaceCurrencyStep()
    assert step("10 kroner", ops) == "10 kroner"


def test_kr_after_amount_still_replaced() -> None:
    ops = NorwegianOperators()
    step = ReplaceCurrencyStep()
    assert step("10 kr", ops) == "10 kroner"
