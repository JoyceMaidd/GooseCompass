"""OTP delivery via the Resend HTTP API."""

import httpx

from backend.config import settings

_RESEND_URL = "https://api.resend.com/emails"


async def send_otp_email(to_email: str, code: str) -> None:
    """Send a one-time verification code to an email address via Resend.

    Args:
        to_email: The recipient's email address.
        code: The plaintext OTP code to send.

    Returns:
        None

    Raises:
        httpx.HTTPStatusError: If Resend responds with a non-2xx status.
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            _RESEND_URL,
            headers={"Authorization": f"Bearer {settings.email_api_key}"},
            json={
                "from": settings.email_from,
                "to": [to_email],
                "subject": "Your GooseCompass verification code",
                "text": (f"Your verification code is {code}. It expires in {settings.otp_ttl_minutes} minutes."),
            },
        )
        response.raise_for_status()
