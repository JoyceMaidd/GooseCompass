from backend.auth.otp import generate_code, hash_code, verify_code_hash
from backend.config import settings


def test_generate_code_length_and_charset():
    """Generated code has the configured length and is all digits."""
    code = generate_code()
    assert len(code) == settings.otp_code_length
    assert code.isdigit()


def test_generate_code_custom_length():
    """generate_code respects an explicit length argument."""
    code = generate_code(length=4)
    assert len(code) == 4
    assert code.isdigit()


def test_generate_code_is_random():
    """Two generated codes are very unlikely to be identical."""
    codes = {generate_code(length=10) for _ in range(5)}
    assert len(codes) == 5


async def test_hash_and_verify_roundtrip():
    """A code verifies successfully against its own hash."""
    code = generate_code()
    code_hash = await hash_code(code)
    assert await verify_code_hash(code, code_hash) is True


async def test_verify_wrong_code_fails():
    """A different code does not verify against an existing hash."""
    code_hash = await hash_code("123456")
    assert await verify_code_hash("654321", code_hash) is False
