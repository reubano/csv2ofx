from datetime import datetime

import pytest

from csv2ofx import Content


@pytest.mark.parametrize("parse_fmt", [None, "%Y-%m-%d"])
@pytest.mark.parametrize("value", [None, "", "not-a-date", 42, "2147483648-01-01"])
def test_invalid_transaction_date_explains_mapping(value, parse_fmt):
    """Invalid dates, such as None, identify the date mapping to check."""
    content = Content({"date": lambda row: value}, parse_fmt=parse_fmt)
    with pytest.raises(ValueError, match="transaction date.*date mapping"):
        content.parse_date({})


@pytest.mark.parametrize(
    "options, value, expected",
    [
        ({}, "2024-01-31", datetime(2024, 1, 31)),
        ({"dayfirst": True}, "01/02/2024", datetime(2024, 2, 1)),
        ({"parse_fmt": "%d.%m.%Y"}, "31.01.2024", datetime(2024, 1, 31)),
    ],
)
def test_valid_transaction_dates(options, value, expected):
    """Valid dates keep existing parsing, e.g. day-first 01/02 means February 1."""
    content = Content({"date": lambda row: value}, **options)
    assert content.parse_date({}) == expected
