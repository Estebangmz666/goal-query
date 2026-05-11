try:
    from src.domain.exceptions.validation_error import ValidationError
except ModuleNotFoundError:
    from domain.exceptions.validation_error import ValidationError


def validate_not_blank(value: str | None, field_name: str) -> None:
    if value is None or not value.strip():
        raise ValidationError(f"{field_name} is required.")


def validate_positive_number(value: float, field_name: str) -> None:
    if value <= 0:
        raise ValidationError(f"{field_name} must be greater than zero.")
