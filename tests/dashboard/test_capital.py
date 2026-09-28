"""Sprint 4 - Day 26 tests for Capital Allocation."""

from src.dashboard.utils.db import (
    get_bs,
    get_cf,
    get_companies,
    get_pl,
    get_ratios,
)


YEAR = "2024-03"
TEST_COMPANY = "TCS"


# ============================================================
# COMPANY DATA
# ============================================================

def test_company_universe():
    companies = get_companies()

    assert companies["company_id"].nunique() == 92


def test_tcs_cashflow_available():
    data = get_cf(TEST_COMPANY)

    assert not data.empty


def test_tcs_balance_sheet_available():
    data = get_bs(TEST_COMPANY)

    assert not data.empty


def test_tcs_ratios_available():
    data = get_ratios(TEST_COMPANY)

    assert not data.empty


def test_tcs_profit_loss_available():
    data = get_pl(TEST_COMPANY)

    assert not data.empty


# ============================================================
# REQUIRED CAPITAL ALLOCATION FIELDS
# ============================================================

def test_cashflow_columns():
    data = get_cf(TEST_COMPANY)

    required = {
        "year",
        "operating_activity",
        "investing_activity",
        "financing_activity",
        "net_cash_flow",
    }

    assert required.issubset(data.columns)


def test_balance_sheet_capital_columns():
    data = get_bs(TEST_COMPANY)

    required = {
        "year",
        "equity_capital",
        "reserves",
        "borrowings",
        "investments",
        "total_assets",
    }

    assert required.issubset(data.columns)


def test_capital_efficiency_columns():
    data = get_ratios(TEST_COMPANY)

    required = {
        "year",
        "roce_pct",
        "asset_turnover",
        "cfo_margin_pct",
        "cfo_pat_ratio",
    }

    assert required.issubset(data.columns)


def test_dividend_payout_column():
    data = get_pl(TEST_COMPANY)

    assert "dividend_payout" in data.columns


# ============================================================
# 2024-03 DATA COVERAGE
# ============================================================

def test_cashflow_2024_coverage():
    companies = get_companies()

    covered = 0

    for company_id in companies["company_id"]:
        data = get_cf(company_id)

        if (
            not data.empty
            and YEAR in set(
                data["year"].astype(str)
            )
        ):
            covered += 1

    assert covered == 90


def test_roce_2024_coverage():
    companies = get_companies()

    covered = 0

    for company_id in companies["company_id"]:
        data = get_ratios(company_id)

        rows = data[
            data["year"].astype(str)
            == YEAR
        ]

        if (
            not rows.empty
            and rows["roce_pct"]
            .notna()
            .any()
        ):
            covered += 1

    assert covered == 89


def test_cfo_margin_2024_coverage():
    companies = get_companies()

    covered = 0

    for company_id in companies["company_id"]:
        data = get_ratios(company_id)

        rows = data[
            data["year"].astype(str)
            == YEAR
        ]

        if (
            not rows.empty
            and rows["cfo_margin_pct"]
            .notna()
            .any()
        ):
            covered += 1

    assert covered == 90


# ============================================================
# SOURCE LIMITATIONS
# ============================================================

def test_fcf_not_fabricated():
    companies = get_companies()

    populated = 0

    for company_id in companies["company_id"]:
        data = get_ratios(company_id)

        rows = data[
            data["year"].astype(str)
            == YEAR
        ]

        if (
            not rows.empty
            and rows["fcf"]
            .notna()
            .any()
        ):
            populated += 1

    assert populated == 0


def test_capex_sales_not_fabricated():
    companies = get_companies()

    populated = 0

    for company_id in companies["company_id"]:
        data = get_ratios(company_id)

        rows = data[
            data["year"].astype(str)
            == YEAR
        ]

        if (
            not rows.empty
            and rows["capex_sales_pct"]
            .notna()
            .any()
        ):
            populated += 1

    assert populated == 0