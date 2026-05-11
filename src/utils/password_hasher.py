from base64 import b64decode, b64encode
from hashlib import pbkdf2_hmac
import hmac
import secrets


class PasswordHasher:
    def __init__(self, iterations: int = 120000) -> None:
        self._iterations = iterations

    def hash_password(self, raw_password: str) -> str:
        salt = secrets.token_bytes(16)
        derived_key = pbkdf2_hmac(
            "sha256",
            raw_password.encode("utf-8"),
            salt,
            self._iterations,
        )
        return (
            f"pbkdf2_sha256${self._iterations}$"
            f"{b64encode(salt).decode('ascii')}$"
            f"{b64encode(derived_key).decode('ascii')}"
        )

    def verify_password(self, raw_password: str, stored_hash: str) -> bool:
        algorithm, iterations, encoded_salt, encoded_key = stored_hash.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False

        derived_key = pbkdf2_hmac(
            "sha256",
            raw_password.encode("utf-8"),
            b64decode(encoded_salt.encode("ascii")),
            int(iterations),
        )
        return hmac.compare_digest(
            derived_key,
            b64decode(encoded_key.encode("ascii")),
        )
