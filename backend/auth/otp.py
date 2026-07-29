"""OTP code generation and bcrypt hashing/verification."""

import asyncio
import secrets

import bcrypt

from backend.config import settings

_DIGITS = "0123456789"


def generate_code(length: int = settings.otp_code_length) -> str:
    """Generate a cryptographically random numeric code.

    Args:
        length: Number of digits in the generated code.

    Returns:
        A string of `length` random digits.
    """
    return "".join(secrets.choice(_DIGITS) for _ in range(length))


async def hash_code(code: str) -> str:
    """Hash a code with bcrypt, offloaded to a thread (CPU-bound work).

    Args:
        code: The plaintext code to hash.

    Returns:
        The bcrypt hash, as a string.
    """
    return await asyncio.to_thread(lambda: bcrypt.hashpw(code.encode(), bcrypt.gensalt()).decode())


async def verify_code_hash(code: str, code_hash: str) -> bool:
    """Check a plaintext code against a bcrypt hash, offloaded to a thread.

    Args:
        code: The plaintext code to check.
        code_hash: The bcrypt hash to check against.

    Returns:
        True if the code matches the hash, False otherwise.
    """
    return await asyncio.to_thread(lambda: bcrypt.checkpw(code.encode(), code_hash.encode()))
