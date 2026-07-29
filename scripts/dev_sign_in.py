"""Dev-only helper: sign in as an @uwaterloo.ca email without Resend configured.

The sign-in UI's code-entry step only appears after a successful
request-code call, and locally (no EMAIL_API_KEY/verified Resend domain)
that call always fails — so the code-entry screen is unreachable through
the browser alone. This script reuses the real request_code/verify_code
logic (domain check, cooldown, hashing, DB insert, JWT issuance), skipping
only the actual email delivery, then prints a devtools console snippet
that plants the resulting session token directly.
"""

import asyncio
import sys

from backend.auth import service
from backend.db import connect_postgres, disconnect_postgres, get_session

_captured_code: str | None = None


async def _capture_code(to_email: str, code: str) -> None:
    global _captured_code
    _captured_code = code


async def run(email: str) -> None:
    """Request and verify a code for `email`, then print a token-planting snippet."""
    service.send_otp_email = _capture_code
    await connect_postgres()
    try:
        async for session in get_session():
            await service.request_code(session, email)
            token = await service.verify_code(session, email, _captured_code)
            break
    finally:
        await disconnect_postgres()

    print(f"\nSigned in as {email}.")
    print("Paste this into your browser's devtools console on the app's tab, then reload:\n")
    print(f"  localStorage.setItem('goosecompass_token', '{token}')\n")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/dev_sign_in.py <email>")
        sys.exit(1)
    asyncio.run(run(sys.argv[1]))
