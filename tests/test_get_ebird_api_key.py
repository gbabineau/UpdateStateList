""" Test the get_ebird_api_key module. """
import pytest

from update_state_list.get_ebird_api_key import (
    EBIRD_API_KEY_NAME,
    get_ebird_api_key,
)


def test_get_ebird_api_key_valid(monkeypatch):
    """ Set a valid API key in the environment variable """
    monkeypatch.setenv(EBIRD_API_KEY_NAME, "valid_api_key")
    assert get_ebird_api_key() == "valid_api_key"


def test_get_ebird_api_key_missing(monkeypatch):
    """ Unset the environment variable """
    monkeypatch.delenv(EBIRD_API_KEY_NAME, raising=False)
    assert get_ebird_api_key() is None


def test_get_ebird_api_key_invalid(monkeypatch):
    """ Set the environment variable to '0' to simulate an invalid key """
    monkeypatch.setenv(EBIRD_API_KEY_NAME, "0")
    with pytest.raises(SystemExit) as exception_info:
        get_ebird_api_key()
    assert exception_info.type is SystemExit
    assert "ebird API key must be specified" in str(exception_info.value)
