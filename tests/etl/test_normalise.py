"""Tests for ETL normalisation."""

from src.etl.normaliser import normalize_ticker, normalize_year


def test_year_mar23():
    assert normalize_year("Mar-23") == "2023-03"


def test_year_fy24():
    assert normalize_year("FY24") == "2024-03"


def test_year_dec22():
    assert normalize_year("Dec-22") == "2022-12"


def test_year_garbage():
    assert normalize_year("xyz") == "PARSE_ERROR"


def test_ticker_strip():
    assert normalize_ticker(" TCS ") == "TCS"


def test_ticker_lower():
    assert normalize_ticker("tcs") == "TCS"


def test_year_space():
    assert normalize_year("Mar 23") == "2023-03"


def test_year_full_month():
    assert normalize_year("March-2023") == "2023-03"


def test_integer_year():
    assert normalize_year(2023) == "2023-03"


def test_normalised_year():
    assert normalize_year("2023-03") == "2023-03"


def test_ticker_hyphen():
    assert normalize_ticker("bajaj-auto") == "BAJAJ-AUTO"


def test_ticker_ampersand():
    assert normalize_ticker("m&m") == "M&M"