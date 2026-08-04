"""Authenticated application identity."""

from dataclasses import dataclass


@dataclass(frozen=True)
class UserContext:
    subject: str
