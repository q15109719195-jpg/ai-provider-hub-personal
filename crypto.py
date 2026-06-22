from __future__ import annotations

import os
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken

from config import KEY_FILE


def get_fernet() -> Fernet:
    key_path = Path(KEY_FILE)
    key_path.parent.mkdir(parents=True, exist_ok=True)

    if not key_path.exists():
        key = Fernet.generate_key()
        key_path.write_bytes(key)
        try:
            os.chmod(key_path, 0o600)
        except OSError:
            pass

    return Fernet(key_path.read_bytes())


def encrypt(value: str) -> str:
    return get_fernet().encrypt(value.encode("utf-8")).decode("utf-8")


def decrypt(value: str) -> str:
    try:
        return get_fernet().decrypt(value.encode("utf-8")).decode("utf-8")
    except (InvalidToken, ValueError, TypeError) as exc:
        raise ValueError("invalid api_key ciphertext") from exc
