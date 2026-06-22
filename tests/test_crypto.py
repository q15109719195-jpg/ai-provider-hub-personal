from __future__ import annotations

from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import crypto


def test_encrypt_then_decrypt_round_trip():
    ciphertext = crypto.encrypt("secret")
    assert crypto.decrypt(ciphertext) == "secret"


def test_encrypt_is_nondeterministic():
    first = crypto.encrypt("secret")
    second = crypto.encrypt("secret")
    assert first != second


def test_decrypt_invalid_ciphertext_raises_value_error():
    with pytest.raises(ValueError, match="invalid api_key ciphertext"):
        crypto.decrypt("invalid-token")
