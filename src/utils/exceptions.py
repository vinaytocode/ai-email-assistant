"""Custom exception classes."""


class EmailAssistantError(Exception):
    """Base exception for email assistant errors."""
    pass


class LLMError(EmailAssistantError):
    """Exception for LLM-related errors."""
    pass


class ValidationError(EmailAssistantError):
    """Exception for validation errors."""
    pass


class ConfigurationError(EmailAssistantError):
    """Exception for configuration errors."""
    pass
