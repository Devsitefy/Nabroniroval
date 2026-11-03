from datetime import date

import pytest

from src.exceptions import CheckInDateEqualsCheckOutException, CheckInDateLaterThanCheckOutException
from src.services.validator import ValidatorService


def test_date_validate_accepts_valid_range():
    ValidatorService.date_validate(date(2027, 1, 1), date(2027, 1, 2))


def test_date_validate_rejects_reversed_range():
    with pytest.raises(CheckInDateLaterThanCheckOutException):
        ValidatorService.date_validate(date(2027, 1, 2), date(2027, 1, 1))


def test_date_validate_rejects_equal_dates():
    with pytest.raises(CheckInDateEqualsCheckOutException):
        ValidatorService.date_validate(date(2027, 1, 1), date(2027, 1, 1))
