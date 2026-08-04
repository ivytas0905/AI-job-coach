"""Clerk bearer-token verification for FastAPI."""

from typing import Any

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ..application.ports.identity import UserContext
from ..config import Settings, get_settings

bearer = HTTPBearer(auto_error=False)


def unauthorized(detail: str = "Invalid authentication credentials") -> HTTPException:
    return HTTPException(status_code=401, detail=detail, headers={"WWW-Authenticate": "Bearer"})


def validate_claims(
    claims: dict[str, Any],
    *,
    issuer: str | None,
    authorized_parties: list[str],
) -> UserContext:
    subject = claims.get("sub")
    if not isinstance(subject, str) or not subject.strip():
        raise unauthorized()
    if issuer and claims.get("iss") != issuer:
        raise unauthorized()
    if authorized_parties and claims.get("azp") not in authorized_parties:
        raise unauthorized()
    return UserContext(subject=subject)


class ClerkTokenVerifier:
    def __init__(self, settings: Settings):
        if not settings.clerk_jwks_url:
            raise RuntimeError("RESUME_CLERK_JWKS_URL is required")
        self.settings = settings
        self.jwks = jwt.PyJWKClient(settings.clerk_jwks_url)

    def verify(self, token: str) -> UserContext:
        try:
            key = self.jwks.get_signing_key_from_jwt(token)
            claims = jwt.decode(
                token,
                key.key,
                algorithms=["RS256"],
                issuer=self.settings.clerk_issuer,
                audience=self.settings.clerk_audience,
                options={"verify_aud": bool(self.settings.clerk_audience)},
            )
        except jwt.PyJWTError as exc:
            raise unauthorized() from exc
        return validate_claims(
            claims,
            issuer=self.settings.clerk_issuer,
            authorized_parties=self.settings.clerk_authorized_parties,
        )


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    settings: Settings = Depends(get_settings),
) -> UserContext:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise unauthorized("Bearer token required")
    return ClerkTokenVerifier(settings).verify(credentials.credentials)


__all__ = ["UserContext", "ClerkTokenVerifier", "get_current_user", "validate_claims"]
