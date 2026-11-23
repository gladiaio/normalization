import pytest

from normalization import load_pipeline
from normalization.languages.registry import get_language_registry
from normalization.languages.russian.operators import RussianOperators


@pytest.fixture
def operators() -> RussianOperators:
    return RussianOperators()


def test_russian_is_registered() -> None:
    assert "ru" in get_language_registry()


def test_russian_registry_produces_russian_operators() -> None:
    instance = get_language_registry()["ru"]()
    assert isinstance(instance, RussianOperators)


def test_config(operators: RussianOperators) -> None:
    assert operators.config.code == "ru"
    assert operators.config.decimal_separator == ","
    assert operators.config.thousand_separator == " "
    assert operators.config.decimal_word is None


def test_expand_written_numbers(operators: RussianOperators) -> None:
    assert operators.expand_written_numbers("двадцать пять") == "25"


# The assertions of issue #52.
def test_issue_52() -> None:
    ru = load_pipeline("gladia-3", "ru")
    assert ru.normalize("двадцать пять") == "25"
    assert ru.normalize("5%") == ru.normalize("пять процентов") == "5 процентов"
    assert ru.normalize("5 км") == ru.normalize("пять километров")
    assert ru.normalize("в 79 году н. э.") == ru.normalize("в 79 году нашей эры")
    assert ru.normalize("до н. э.") == ru.normalize("до нашей эры")
    assert ru.normalize("э ну я думаю") == "ну я думаю"
    assert ru.normalize("эм ну я думаю") == "ну я думаю"


@pytest.mark.parametrize(
    "filler", ["э", "ээ", "эээ", "эм", "мм", "ммм", "м-м", "хм", "гм"]
)
def test_fillers_are_removed(filler: str) -> None:
    assert load_pipeline("gladia-3", "ru").normalize(f"{filler} я думаю") == "я думаю"


@pytest.mark.parametrize("text", ["ну я думаю", "а я думаю", "в к с"])
def test_words_are_kept(text: str) -> None:
    assert load_pipeline("gladia-3", "ru").normalize(text) == text


def test_millimetre_is_not_a_filler_after_a_number() -> None:
    ru = load_pipeline("gladia-3", "ru")
    assert ru.normalize("5 мм") == ru.normalize("пять миллиметров") == "5 миллиметров"
    assert ru.normalize("мм ну я думаю") == "ну я думаю"
