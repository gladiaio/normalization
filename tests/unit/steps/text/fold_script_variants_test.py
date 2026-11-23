from normalization.languages import get_language_registry
from normalization.languages.base import LanguageOperators
from normalization.steps.text.fold_script_variants import FoldScriptVariantsStep

from .conftest import assert_text_step_registered


def test_step_is_registered():
    assert_text_step_registered(FoldScriptVariantsStep)


def test_no_op_by_default(operators: LanguageOperators):
    assert FoldScriptVariantsStep()("コロコロ 人々", operators) == "コロコロ 人々"


def test_only_japanese_folds():
    registry = get_language_registry()
    for code, operators_cls in registry.items():
        folded = FoldScriptVariantsStep()("コロコロ", operators_cls())
        assert folded == ("ころころ" if code == "ja" else "コロコロ"), code
