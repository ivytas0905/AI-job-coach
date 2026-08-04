from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import HTTPException

from agent_service.api.auth import ClerkTokenVerifier, UserContext, validate_claims
from agent_service.config import Settings


def test_valid_claims_return_verified_subject():
    context = validate_claims(
        {"sub": "user_123", "iss": "https://clerk.example", "azp": "http://localhost:3000"},
        issuer="https://clerk.example",
        authorized_parties=["http://localhost:3000"],
    )
    assert context == UserContext(subject="user_123")


@pytest.mark.parametrize("claims", [{}, {"sub": ""}, {"sub": "user", "iss": "wrong"}])
def test_invalid_subject_or_issuer_fails_closed(claims):
    with pytest.raises(HTTPException) as error:
        validate_claims(claims, issuer="https://clerk.example", authorized_parties=[])
    assert error.value.status_code == 401


def test_wrong_authorized_party_fails_closed():
    with pytest.raises(HTTPException) as error:
        validate_claims(
            {"sub": "user", "iss": "https://clerk.example", "azp": "https://evil.example"},
            issuer="https://clerk.example",
            authorized_parties=["http://localhost:3000"],
        )
    assert error.value.status_code == 401


def _token_verifier():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    settings = Settings(
        clerk_jwks_url="https://clerk.example/.well-known/jwks.json",
        clerk_issuer="https://clerk.example",
        clerk_audience="resume-api",
        clerk_authorized_parties=["http://localhost:3000"],
    )
    verifier = ClerkTokenVerifier(settings)
    verifier.jwks.get_signing_key_from_jwt = lambda _: SimpleNamespace(
        key=private_key.public_key()
    )
    return verifier, private_key


def test_verifier_accepts_valid_signed_token():
    verifier, private_key = _token_verifier()
    token = jwt.encode(
        {
            "sub": "user_123",
            "iss": "https://clerk.example",
            "aud": "resume-api",
            "azp": "http://localhost:3000",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
        },
        private_key,
        algorithm="RS256",
    )

    assert verifier.verify(token) == UserContext(subject="user_123")


@pytest.mark.parametrize(
    ("claim", "value"),
    [
        ("iss", "https://wrong.example"),
        ("aud", "wrong-api"),
        ("exp", datetime.now(timezone.utc) - timedelta(minutes=5)),
    ],
)
def test_verifier_rejects_invalid_standard_claims(claim, value):
    verifier, private_key = _token_verifier()
    claims = {
        "sub": "user_123",
        "iss": "https://clerk.example",
        "aud": "resume-api",
        "azp": "http://localhost:3000",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
    }
    claims[claim] = value
    token = jwt.encode(claims, private_key, algorithm="RS256")

    with pytest.raises(HTTPException) as error:
        verifier.verify(token)

    assert error.value.status_code == 401


def test_verifier_rejects_token_with_wrong_signature():
    verifier, _ = _token_verifier()
    attacker_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    token = jwt.encode(
        {
            "sub": "user_123",
            "iss": "https://clerk.example",
            "aud": "resume-api",
            "azp": "http://localhost:3000",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
        },
        attacker_key,
        algorithm="RS256",
    )

    with pytest.raises(HTTPException) as error:
        verifier.verify(token)

    assert error.value.status_code == 401
