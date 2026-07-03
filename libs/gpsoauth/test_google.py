import base64
from unittest.mock import patch, MagicMock

import pytest

from libs.gpsoauth.google import (
    construct_signature,
    key_from_b64,
    key_to_struct,
    parse_auth_response,
)


def test_parse_auth_response():
    """Test parsing of the authentication response."""
    # Test normal response
    response_text = "Auth=12345\nToken=abcde\n"
    expected = {"Auth": "12345", "Token": "abcde"}
    assert parse_auth_response(response_text) == expected

    # Test empty response
    assert parse_auth_response("") == {}

    # Test line with multiple equal signs
    assert parse_auth_response("Key=Value=More") == {"Key": "Value=More"}

    # Test with multiple empty lines
    assert parse_auth_response("\n\nAuth=123\n\n") == {"Auth": "123"}


@patch("libs.gpsoauth.google.RSA.construct")
def test_key_from_b64(mock_rsa_construct):
    """Test extracting a key from base64."""
    # i = 4 bytes (e.g. length 2) -> 2
    # mod = 2 bytes -> b"\x01\x02" -> 258
    # j = 4 bytes (e.g. length 1) -> 1
    # exponent = 1 byte -> b"\x03" -> 3
    binary_key = b"\x00\x00\x00\x02" + b"\x01\x02" + b"\x00\x00\x00\x01" + b"\x03"
    b64_key = base64.b64encode(binary_key)

    mock_rsa_construct.return_value = "mock_key"

    result = key_from_b64(b64_key)

    # 0x0102 = 258
    # 0x03 = 3
    mock_rsa_construct.assert_called_once_with((258, 3))
    assert result == "mock_key"


def test_key_to_struct():
    """Test converting a key to struct."""
    mock_key = MagicMock()
    # Using 258 (b'\x01\x02') for n and 3 (b'\x03') for e
    mock_key.n = 258
    mock_key.e = 3

    result = key_to_struct(mock_key)

    expected = b"\x00\x00\x00\x80\x01\x02\x00\x00\x00\x03\x03"
    assert result == expected


@patch("libs.gpsoauth.google.PKCS1_OAEP.new")
def test_construct_signature(mock_pkcs_new):
    """Test signature construction."""
    mock_key = MagicMock()
    # Mocking key.n and key.e so key_to_struct doesn't crash
    mock_key.n = 258
    mock_key.e = 3

    email = "test@example.com"
    password = "mypassword"

    mock_cipher = MagicMock()
    mock_cipher.encrypt.return_value = b"encrypted_payload"
    mock_pkcs_new.return_value = mock_cipher

    signature_b64 = construct_signature(email, password, mock_key)

    # Verify PKCS1_OAEP cipher was created with the correct key
    mock_pkcs_new.assert_called_once_with(mock_key)

    # Verify cipher encrypt was called with the correct formatted string
    expected_plaintext = b"test@example.com\x00mypassword"
    mock_cipher.encrypt.assert_called_once_with(expected_plaintext)

    # Decode signature to verify its contents
    signature = base64.urlsafe_b64decode(signature_b64)

    # Signature should start with \x00
    assert signature[0] == 0x00

    # Signature should end with the encrypted payload
    assert signature[-len(b"encrypted_payload"):] == b"encrypted_payload"

    # Overall signature length should be 1 + 4 (hash of struct) + len(encrypted_payload)
    assert len(signature) == 1 + 4 + len(b"encrypted_payload")
