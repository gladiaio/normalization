from normalization.languages.english import EnglishOperators
from normalization.steps.text.convert_dots_to_words_in_technical_contexts import (
    ConvertDotsToWordsInTechnicalContextsStep,
)

from .conftest import assert_text_step_registered


def test_step_is_registered():
    assert_text_step_registered(ConvertDotsToWordsInTechnicalContextsStep)


def test_ip_address_conversion(english_operators: EnglishOperators):
    """
    Test that the ip address conversion converts the ip address to the language ip address word.
    """
    text = "192.168.1.1"
    converted_text = ConvertDotsToWordsInTechnicalContextsStep()(
        text, english_operators
    )
    assert converted_text == "192 dot 168 dot 1 dot 1"


def test_domain_conversion(english_operators: EnglishOperators):
    """
    Test that the domain conversion converts the domain to the language domain word.
    """
    text = "example.com"
    converted_text = ConvertDotsToWordsInTechnicalContextsStep()(
        text, english_operators
    )
    assert converted_text == "example dot com"


def test_file_extension_conversion(english_operators: EnglishOperators):
    """
    Test that the file extension conversion converts the file extension to the language file extension word.
    """
    text = "example.txt"
    converted_text = ConvertDotsToWordsInTechnicalContextsStep()(
        text, english_operators
    )
    assert converted_text == "example dot txt"


def test_version_conversion(english_operators: EnglishOperators):
    """
    Test that the version conversion converts the version to the language version word.
    """
    text = "1.0.0"
    converted_text = ConvertDotsToWordsInTechnicalContextsStep()(
        text, english_operators
    )
    assert converted_text == "1 dot 0 dot 0"
