"""Exceptions for Runbox client."""

from __future__ import annotations


class RunboxError(Exception):
    """Base exception for Runbox client."""
    pass


class ConfigurationError(RunboxError):
    """Configuration error."""
    pass


class ConnectionError(RunboxError):
    """Connection error."""
    pass


class AuthenticationError(RunboxError):
    """Authentication error (401)."""
    pass


class NotFoundError(RunboxError):
    """Not found error (404)."""
    pass


class ValidationError(RunboxError):
    """Validation error (400)."""
    
    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message)
        self.details = details


class RunError(RunboxError):
    """Run error (500)."""
    pass
