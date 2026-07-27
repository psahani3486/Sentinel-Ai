"""
Sentinel AI — Custom Exception Hierarchy

All domain-specific exceptions inherit from SentinelException.
The global error handler (middleware/error_handler.py) maps each
exception type to the appropriate HTTP status code and JSON body.
"""

from typing import Any


class SentinelException(Exception):
    """Base exception for all Sentinel AI domain errors."""

    def __init__(self, message: str, details: Any = None) -> None:
        self.message = message
        self.details = details
        super().__init__(self.message)


class EntityNotFoundException(SentinelException):
    """Raised when a requested entity does not exist."""

    def __init__(self, entity_type: str, entity_id: Any) -> None:
        super().__init__(
            message=f"{entity_type} with id '{entity_id}' not found",
            details={"entity_type": entity_type, "entity_id": str(entity_id)},
        )


class DuplicateEntityException(SentinelException):
    """Raised when a unique constraint would be violated."""

    def __init__(self, entity_type: str, field: str, value: Any) -> None:
        super().__init__(
            message=f"{entity_type} with {field} '{value}' already exists",
            details={"entity_type": entity_type, "field": field, "value": str(value)},
        )


class AuthenticationException(SentinelException):
    """Raised when authentication fails (bad credentials, expired token)."""

    def __init__(self, message: str = "Invalid credentials") -> None:
        super().__init__(message=message)


class AuthorizationException(SentinelException):
    """Raised when the authenticated user lacks the required role."""

    def __init__(self, required_role: str | None = None) -> None:
        message = "Insufficient permissions"
        details: dict[str, Any] = {}
        if required_role:
            message = f"Insufficient permissions. Required role: {required_role}"
            details["required_role"] = required_role
        super().__init__(message=message, details=details)


class TokenException(SentinelException):
    """Raised when JWT validation fails."""

    def __init__(self, message: str = "Invalid or expired token") -> None:
        super().__init__(message=message)


class ValidationException(SentinelException):
    """Raised for business-rule validation failures (not schema validation)."""

    def __init__(self, message: str, errors: list[dict[str, Any]] | None = None) -> None:
        super().__init__(message=message, details={"errors": errors or []})


# ── Connector Framework Exceptions ───────────────────────────────────────────

class ConnectorError(SentinelException):
    """Base exception for all connector-related failures."""

    def __init__(self, message: str, details: Any = None) -> None:
        super().__init__(message=message, details=details)


class ConnectionError(ConnectorError):
    """Raised when establishing a connection to a data source fails."""

    def __init__(self, message: str, details: Any = None) -> None:
        super().__init__(message=f"Connector Connection Failure: {message}", details=details)


class ConfigurationError(ConnectorError):
    """Raised when connector parameters or settings are invalid or missing."""

    def __init__(self, message: str, errors: list[str] | None = None) -> None:
        super().__init__(
            message=f"Connector Configuration Invalid: {message}",
            details={"validation_errors": errors or []},
        )


class SchemaDiscoveryError(ConnectorError):
    """Raised when schema extraction or type inference fails."""

    def __init__(self, message: str, details: Any = None) -> None:
        super().__init__(message=f"Schema Discovery Failure: {message}", details=details)


class ReadError(ConnectorError):
    """Raised when reading or streaming data chunks from a source fails."""

    def __init__(self, message: str, details: Any = None) -> None:
        super().__init__(message=f"Data Read Failure: {message}", details=details)
