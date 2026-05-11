class DatabaseConfigurationError(Exception):
    """Raised when database configuration is incomplete or invalid."""


class DatabaseConnectionError(Exception):
    """Raised when the application cannot connect to SQL Server."""


class DatabaseExecutionError(Exception):
    """Raised when a SQL statement or script cannot be executed."""
