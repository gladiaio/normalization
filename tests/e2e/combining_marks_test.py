"""gladia-3 keeps the words of scripts whose combining marks belong to the letter (#49), and
folds the others exactly as 0.4.0 did."""

import pytest

from normalization import load_pipeline


@pytest.mark.parametrize(
    ("language", "text", "expected"),
    [
        (
            "hi",
            "लूना को साथी पहलवानों ने भी श्रद्धांजलि दी.",
            "लूना को साथी पहलवानों ने भी श्रद्धांजलि दी",
        ),
        ("bn", "আমি বাংলায় গান গাই।", "আমি বাংলায় গান গাই"),
        ("he", "שָׁלוֹם", "שלום"),
        ("he", 'צה"ל וצה״ל', "צהל וצהל"),
        ("ja", "です が パ", "です が ぱ"),  # katakana folds to hiragana (#58)
        ("ru", "двойной", "двойной"),
        ("ru", "Ёлка", "елка"),
    ],
)
def test_combining_marks_keep_the_word(language: str, text: str, expected: str) -> None:
    assert load_pipeline("gladia-3", language).normalize(text) == expected


def test_combining_marks_keep_the_word_count() -> None:
    text = "लूना को साथी पहलवानों ने भी श्रद्धांजलि दी."
    assert len(load_pipeline("gladia-3", "hi").normalize(text).split()) == len(
        text.split()
    )


# Outputs of gladia-normalization 0.4.0 (b58bb4f), recorded before the change: the scripts whose
# marks are diacritics fold exactly as before.
@pytest.mark.parametrize(
    ("language", "text", "expected"),
    [
        ("fr", "Café élève à l'école, où est-ce ?", "cafe eleve a l ecole ou est ce"),
        (
            "en",
            "The naïve café owner's résumé, 6.5 percent.",
            "the naive cafe owner s resume 6 point 5 percent",
        ),
        ("en", "Ça va très bien, Zoë.", "ca va tres bien zoe"),
        ("en", "Ελληνικά άλφα έψιλον", "ελληνικα αλφα εψιλον"),
        ("ru", "Ёлка и ёжик", "елка и ежик"),
        ("ar", "ذَهَبَ الوَلَدُ إِلَى المَدْرَسَةِ", "ذهب الولد الي المدرسه"),
        ("ar", "مُحَمَّدٌ رَسُولُ اللَّهِ", "محمد رسول الله"),
        ("de", "Größe, Übermaß und Straße.", "grosse ubermass und strasse"),
        ("da", "Blåbærgrød på Østerbro.", "blabaergrod pa osterbro"),
        ("fi", "Hyvää päivää, äiti.", "hyvaa paivaa aiti"),
    ],
)
def test_folds_unchanged_from_0_4_0(language: str, text: str, expected: str) -> None:
    assert load_pipeline("gladia-3", language).normalize(text) == expected
