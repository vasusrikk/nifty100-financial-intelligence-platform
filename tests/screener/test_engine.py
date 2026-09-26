import pytest

from src.screener.engine import (
    SUPPORTED_FILTERS,
    apply_filter,
    apply_filters,
    compare_numeric,
    is_debt_free,
    is_financial,
    load_screener_data,
    row_passes_filter,
)


# ============================================================
# BASIC CONFIGURATION
# ============================================================

def test_supported_filter_count():
    assert len(SUPPORTED_FILTERS) == 15


def test_required_filters_exist():
    expected = {
        "roe_pct",
        "roce_pct",
        "npm_pct",
        "opm_pct",
        "de_ratio",
        "icr",
        "asset_turnover",
        "revenue_cagr_5yr",
        "pat_cagr_5yr",
        "eps_cagr_5yr",
        "cfo_margin_pct",
        "pe_ratio",
        "pb_ratio",
        "dividend_yield_pct",
        "market_cap_crore",
    }

    assert SUPPORTED_FILTERS == expected


# ============================================================
# NUMERIC COMPARISON
# ============================================================

def test_numeric_comparisons():
    assert compare_numeric(20, ">", 15)
    assert compare_numeric(15, ">=", 15)
    assert compare_numeric(10, "<", 15)
    assert compare_numeric(15, "<=", 15)
    assert compare_numeric(15, "==", 15)
    assert compare_numeric(10, "!=", 15)


def test_missing_numeric_value_fails():
    assert compare_numeric(None, ">", 10) is False


def test_invalid_operator():
    with pytest.raises(ValueError):
        compare_numeric(
            10,
            "INVALID",
            5,
        )


# ============================================================
# FINANCIAL-SECTOR HANDLING
# ============================================================

def test_financial_sector_detection():
    row = {
        "broad_sector": "Financials"
    }

    assert is_financial(row) is True


def test_non_financial_sector_detection():
    row = {
        "broad_sector": "Industrials"
    }

    assert is_financial(row) is False


def test_financials_de_carveout():
    row = {
        "broad_sector": "Financials",
        "de_ratio": 12.0,
        "icr_flag": "NORMAL",
    }

    assert row_passes_filter(
        row,
        "de_ratio",
        "<",
        1,
    ) is True


def test_non_financial_de_filter():
    row = {
        "broad_sector": "Industrials",
        "de_ratio": 2.0,
        "icr_flag": "NORMAL",
    }

    assert row_passes_filter(
        row,
        "de_ratio",
        "<",
        1,
    ) is False


# ============================================================
# DEBT-FREE ICR HANDLING
# ============================================================

def test_debt_free_flag_detection():
    row = {
        "icr_flag": "DEBT_FREE",
        "de_ratio": 0.5,
    }

    assert is_debt_free(row) is True


def test_zero_debt_detection():
    row = {
        "icr_flag": "NORMAL",
        "de_ratio": 0.0,
    }

    assert is_debt_free(row) is True


def test_debt_free_passes_minimum_icr():
    row = {
        "broad_sector": "Industrials",
        "de_ratio": 0.0,
        "icr": None,
        "icr_flag": "DEBT_FREE",
    }

    assert row_passes_filter(
        row,
        "icr",
        ">",
        3,
    ) is True


# ============================================================
# FILTER PIPELINE
# ============================================================

def test_multiple_filters():
    rows = [
        {
            "company_id": "A",
            "broad_sector": "Industrials",
            "roe_pct": 20,
            "de_ratio": 0.5,
            "icr_flag": "NORMAL",
        },
        {
            "company_id": "B",
            "broad_sector": "Industrials",
            "roe_pct": 10,
            "de_ratio": 0.5,
            "icr_flag": "NORMAL",
        },
    ]

    result = apply_filters(
        rows,
        [
            {
                "metric": "roe_pct",
                "operator": ">",
                "value": 15,
            },
            {
                "metric": "de_ratio",
                "operator": "<",
                "value": 1,
            },
        ],
    )

    assert len(result) == 1
    assert result[0]["company_id"] == "A"


def test_unsupported_metric():
    rows = [
        {
            "company_id": "A"
        }
    ]

    with pytest.raises(ValueError):
        apply_filter(
            rows,
            "fake_metric",
            ">",
            1,
        )


# ============================================================
# DATABASE INTEGRATION
# ============================================================

def test_latest_usable_company_rows_unique():
    rows = load_screener_data()

    company_ids = [
        row["company_id"]
        for row in rows
    ]

    assert len(company_ids) == len(
        set(company_ids)
    )


def test_latest_usable_universe_not_empty():
    rows = load_screener_data()

    assert len(rows) > 0


def test_abb_uses_usable_period():
    rows = load_screener_data()

    abb = next(
        row
        for row in rows
        if row["company_id"] == "ABB"
    )

    assert abb["year"] == "2024-03"
    assert abb["roe_pct"] is not None


def test_financial_companies_exist():
    rows = load_screener_data()

    financials = [
        row
        for row in rows
        if is_financial(row)
    ]

    assert len(financials) > 0