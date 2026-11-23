import pytest

from normalization.languages.japanese import JapaneseOperators
from normalization.languages.japanese.script_fold import fold_japanese_script


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("コロコロ", "ころころ"),
        ("ヴァイオリン", "ゔぁいおりん"),
        ("ヵ", "ゕ"),
        ("ヶ", "ゖ"),
        ("ァィゥェォ", "ぁぃぅぇぉ"),
    ],
)
def test_katakana_folds_to_hiragana(text: str, expected: str) -> None:
    assert fold_japanese_script(text) == expected


def test_katakana_without_hiragana_is_kept() -> None:
    assert fold_japanese_script("ヷヸヹヺ") == "ヷヸヹヺ"


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("コンピューター", "こんぴゅーた"),
        ("スーパー", "すーぱ"),
        ("コンピューターを使う", "こんぴゅーたを使う"),
        ("ハード", "はーど"),  # a ー inside the word stays
        ("ラーメン", "らーめん"),
        ("あー", "あー"),  # not a katakana word
    ],
)
def test_word_final_prolonged_sound_mark(text: str, expected: str) -> None:
    assert fold_japanese_script(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("人々", "人人"),
        ("時々刻々", "時時刻刻"),
        ("々", "々"),  # at the start of a string
        ("あ々", "あ々"),  # not after a kanji
    ],
)
def test_iteration_mark(text: str, expected: str) -> None:
    assert fold_japanese_script(text) == expected


@pytest.mark.parametrize("text", ["3ヶ月", "3ヵ月", "3か月", "３ヶ月", "3箇月"])
def test_counter_after_a_digit(text: str) -> None:
    assert fold_japanese_script(text).endswith("か月")


@pytest.mark.parametrize(
    ("text", "expected"),
    [("三ヶ所", "三か所"), ("数箇所", "数か所"), ("何ヵ月", "何か月")],
)
def test_counter_after_a_kanji_numeral(text: str, expected: str) -> None:
    assert fold_japanese_script(text) == expected


def test_counter_variant_not_after_a_number() -> None:
    # 箇条 is a word, not a counter after a number.
    assert fold_japanese_script("箇条") == "箇条"


def test_decomposed_input_is_composed_first() -> None:
    assert fold_japanese_script("ピアノ") == "ぴあの"


def test_mixed_kanji_and_katakana() -> None:
    assert fold_japanese_script("東京タワーに行く") == "東京たわに行く"


def test_kanji_and_hiragana_untouched() -> None:
    assert fold_japanese_script("鳴った") == "鳴った"
    assert fold_japanese_script("箸と橋") == "箸と橋"


def test_operator_delegates() -> None:
    assert JapaneseOperators().fold_script_variants("コロコロ") == "ころころ"
