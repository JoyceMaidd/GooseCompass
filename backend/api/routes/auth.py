"""POST /auth/request-code and POST /auth/verify-code routes."""

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth import service
from backend.db import get_session
from backend.monitoring.rate_limit import limiter

router = APIRouter(prefix="/auth")


class RequestCodeRequest(BaseModel):
    """Payload for POST /auth/request-code.

    Args:
        email: The address to send a one-time code to.
    """

    email: str


class VerifyCodeRequest(BaseModel):
    """Payload for POST /auth/verify-code.

    Args:
        email: The address being verified.
        code: The one-time code the user received.
    """

    email: str
    code: str


class VerifyCodeResponse(BaseModel):
    """Response for a successful POST /auth/verify-code.

    Args:
        access_token: The issued JWT session token.
        token_type: Always "bearer".
    """

    access_token: str
    token_type: str = "bearer"


@router.post("/request-code", status_code=204)
@limiter.limit("5/60s")
async def request_code_route(
    request: Request,
    payload: RequestCodeRequest,
    session: AsyncSession = Depends(get_session),
) -> None:
    """Request a one-time code be emailed to a @uwaterloo.ca address.

    Rate-limited to 5 requests per 60 seconds per IP.

    Args:
        request: FastAPI request (for rate limiting).
        payload: The request payload containing the target email.
        session: An open Postgres async session.

    Returns:
        None

    Raises:
        HTTPException: 400 if the email is not a @uwaterloo.ca address,
            429 if requested again within the resend cooldown window or
            if rate limit is exceeded.
    """
    try:
        await service.request_code(session, payload.email)
    except service.DomainError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except service.CooldownError as e:
        raise HTTPException(status_code=429, detail=str(e))


@router.post("/verify-code", response_model=VerifyCodeResponse)
async def verify_code_route(
    payload: VerifyCodeRequest, session: AsyncSession = Depends(get_session)
) -> VerifyCodeResponse:
    """Verify a one-time code and issue a session token.

    Args:
        payload: The request payload containing the email and code.
        session: An open Postgres async session.

    Returns:
        A VerifyCodeResponse carrying the issued JWT.

    Raises:
        HTTPException: 401 if the code is invalid, expired, or exhausted.
    """
    try:
        token = await service.verify_code(session, payload.email, payload.code)
    except service.InvalidCodeError as e:
        raise HTTPException(status_code=401, detail=str(e))
    return VerifyCodeResponse(access_token=token)
