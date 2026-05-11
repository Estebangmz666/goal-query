"""Domain exceptions package."""

try:
    from src.domain.exceptions.validation_error import ValidationError
except ModuleNotFoundError:
    from domain.exceptions.validation_error import ValidationError
