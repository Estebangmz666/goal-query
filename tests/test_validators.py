import unittest

try:
    from src.domain.exceptions.validation_error import ValidationError
    from src.utils.validators import validate_not_blank, validate_positive_number
except ModuleNotFoundError:
    from domain.exceptions.validation_error import ValidationError
    from utils.validators import validate_not_blank, validate_positive_number


class ValidatorsTestCase(unittest.TestCase):
    def test_validate_not_blank_rejects_blank_values(self) -> None:
        with self.assertRaises(ValidationError):
            validate_not_blank("   ", "Username")

    def test_validate_positive_number_rejects_zero(self) -> None:
        with self.assertRaises(ValidationError):
            validate_positive_number(0, "Team weight")


if __name__ == "__main__":
    unittest.main()
