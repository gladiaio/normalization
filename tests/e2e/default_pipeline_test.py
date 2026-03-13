from normalization.pipeline.loader import load_pipeline


def test_default_pipeline():
    """
    Test that the default pipeline normalizes the text correctly.
    """
    pipeline = load_pipeline("gladia-3", "default")
    assert pipeline.normalize("Hello, world!") == "hello world"


def test_unknown_language():
    """
    Test that the default pipeline raises an error for an unknown language.
    """
    pipeline = load_pipeline("gladia-3", "unknown")
    assert pipeline.normalize("ça va?!") == "ca va"


def test_currency_sign_is_not_normalized():
    """
    Test that the default pipeline does not normalize currency signs.
    """
    pipeline = load_pipeline("gladia-3", "default")
    assert pipeline.normalize("$100") == "$100"
    assert pipeline.normalize("80 €") == "80 €"


def test_email_adresses_not_normalized():
    """
    Test that the default pipeline does not normalize email addresses.
    """
    pipeline = load_pipeline("gladia-3", "default")
    assert pipeline.normalize("test@example.com") == "test@example.com"


def test_phone_numbers_not_normalized():
    """
    Test that the default pipeline does not normalize phone numbers.
    """
    pipeline = load_pipeline("gladia-3", "default")
    assert pipeline.normalize("+1234567890") == "+1234567890"
