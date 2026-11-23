"""Word-level substitutions for Hindi.

Word replacements run after normalize_spelling_variants, so keys and values are
written in its output form: anusvara for chandrabindu, no nukta on क ख ग ज फ.

The entries fold the "श्रुतिमूलक य" (glide य) of verb forms to the vowel, as the
standard Hindi orthography of the Central Hindi Directorate prescribes (rule
3.14.1: गया - गई - गए, not गयी / गये): both spellings of each word are in use.
The list is closed on purpose: a general "य + vowel sign -> vowel" rule would
merge distinct words (गायें "cows" and गाएं "may sing", दिये "lamps" and दिए
"gave"). The nouns and adjectives whose य belongs to the stem (रुपया, किराया,
नया) are folded too: their two spellings are one word, and no other word has the
folded form.
"""

HINDI_REPLACEMENTS: dict[str, str] = {
    # जाना / आना / करना / लेना / पीना / होना / चाहना: past and subjunctive forms
    "गये": "गए",
    "गयी": "गई",
    "गयीं": "गईं",
    "आये": "आए",
    "आयी": "आई",
    "आयीं": "आईं",
    "आयें": "आएं",
    "किये": "किए",
    "लिये": "लिए",
    "पिये": "पिए",
    "हुये": "हुए",
    "चाहिये": "चाहिए",
    # Stem य: the same word written both ways
    "नये": "नए",
    "नयी": "नई",
    "रुपये": "रुपए",
    "किराये": "किराए",
}
