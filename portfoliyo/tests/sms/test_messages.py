from portfoliyo.sms import messages



def test_get_default_language():
    """If requested msg not found in requested language, gets default lang."""
    assert messages.get('UNKNOWN', 'foo') == messages.get('UNKNOWN', 'en')
