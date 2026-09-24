from datetime import date, datetime

import pandas as pd
import pytest

from src.etl.normaliser import normalize_ticker, normalize_year


# ============================================================
# SPRINT 1 - NORMALIZATION TESTS
# Requirement:
#   20 normalize_year cases
#   20 normalize_ticker cases
# ============================================================


# ------------------------------------------------------------
# normalize_year - 20 test cases
# ------------------------------------------------------------

@pytest.mark.parametrize(
    "input_value, expected",
    [
        # 1
        ("Mar-23", "2023-03"),

        # 2
        ("FY24", "2024-03"),

        # 3
        ("Dec-22", "2022-12"),

        # 4
        ("garbage", "PARSE_ERROR"),

        # 5
        (" Mar-23 ", "2023-03"),

        # 6
        ("March-2023", "2023-03"),

        # 7
        (2023, "2023-03"),

        # 8
        (2024.0, "2024-03"),

        # 9
        ("2023", "2023-03"),

        # 10
        ("2023-03", "2023-03"),

        # 11
        ("FY 23", "2023-03"),

        # 12
        ("fy25", "2025-03"),

        # 13
        ("FY2026", "2026-03"),

        # 14
        ("Sep-21", "2021-09"),

        # 15
        ("September-2021", "2021-09"),

        # 16
        ("March 2020", "2020-03"),

        # 17
        (datetime(2019, 6, 15), "2019-06"),

        # 18
        (date(2018, 12, 31), "2018-12"),

        # 19
        (pd.Timestamp("2017-04-01"), "2017-04"),

        # 20
        (None, "PARSE_ERROR"),
    ],
)
def test_normalize_year_20_cases(input_value, expected):
    assert normalize_year(input_value) == expected


# ------------------------------------------------------------
# normalize_ticker - 20 test cases
# ------------------------------------------------------------

@pytest.mark.parametrize(
    "input_value, expected",
    [
        # 1
        ("reliance", "RELIANCE"),

        # 2
        (" RELIANCE ", "RELIANCE"),

        # 3
        ("tcs", "TCS"),

        # 4
        (" TCS", "TCS"),

        # 5
        ("INFY ", "INFY"),

        # 6
        ("hdfcbank", "HDFCBANK"),

        # 7
        ("HDFC BANK", "HDFC BANK"),

        # 8
        ("BAJAJ-AUTO", "BAJAJ-AUTO"),

        # 9
        ("m&m", "M&M"),

        # 10
        ("M&M", "M&M"),

        # 11
        ("lt", "LT"),

        # 12
        ("adaniensol", "ADANIENSOL"),

        # 13
        ("  icicibank  ", "ICICIBANK"),

        # 14
        ("sbin", "SBIN"),

        # 15
        ("123", "123"),

        # 16
        ("abc.def", "ABC.DEF"),

        # 17
        ("abc_123", "ABC_123"),

        # 18
        ("", "MISSING"),

        # 19
        ("   ", "MISSING"),

        # 20
        (None, "MISSING"),
    ],
)
def test_normalize_ticker_20_cases(input_value, expected):
    assert normalize_ticker(input_value) == expected