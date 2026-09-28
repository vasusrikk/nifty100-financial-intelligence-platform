"""Sprint 4 - Day 23 tests for Home and Company Profile data."""

from src.dashboard.utils.db import (
    get_companies,
    get_home_snapshot,
    get_home_summary,
    get_pl,
    get_bs,
    get_cf,
    get_ratios,
    get_valuation,
)


YEAR = "2024-03"
TEST_COMPANY = "TCS"


# ============================================================
# HOME TESTS
# ============================================================

def test_company_universe_is_92():
    companies = get_companies()

    assert len(companies) == 92
    assert companies["company_id"].nunique() == 92


def test_home_snapshot_has_92_companies():
    snapshot = get_home_snapshot(YEAR)

    assert len(snapshot) == 92
    assert snapshot["company_id"].nunique() == 92


def test_home_summary_required_fields():
    summary = get_home_summary(YEAR)

    required = {
        "average_roe",
        "median_pe",
        "median_de",
        "total_companies",
        "median_revenue_cagr_5yr",
        "debt_free_companies",
        "ratio_coverage",
        "market_cap_coverage",
    }

    assert required.issubset(summary.keys())


def test_home_total_companies():
    summary = get_home_summary(YEAR)

    assert summary["total_companies"] == 92


def test_home_ratio_coverage():
    summary = get_home_summary(YEAR)

    assert summary["ratio_coverage"] == 91


def test_home_market_cap_coverage():
    summary = get_home_summary(YEAR)

    assert summary["market_cap_coverage"] == 92


def test_home_median_pe():
    summary = get_home_summary(YEAR)

    assert round(summary["median_pe"], 2) == 46.18


def test_home_median_de():
    summary = get_home_summary(YEAR)

    assert round(summary["median_de"], 2) == 0.44


def test_home_median_revenue_cagr():
    summary = get_home_summary(YEAR)

    assert round(
        summary["median_revenue_cagr_5yr"],
        2,
    ) == 12.03


def test_home_debt_free_count():
    summary = get_home_summary(YEAR)

    assert summary["debt_free_companies"] == 3


def test_home_average_roe():
    summary = get_home_summary(YEAR)

    assert round(
        summary["average_roe"],
        2,
    ) == 125.08


# ============================================================
# COMPANY PROFILE TESTS
# ============================================================

def test_tcs_exists():
    companies = get_companies()

    assert TEST_COMPANY in set(
        companies["company_id"]
    )


def test_tcs_ratios_available():
    ratios = get_ratios(TEST_COMPANY)

    assert not ratios.empty
    assert len(ratios) >= 1


def test_tcs_profit_and_loss_available():
    pl = get_pl(TEST_COMPANY)

    assert not pl.empty
    assert len(pl) >= 1


def test_tcs_balance_sheet_available():
    bs = get_bs(TEST_COMPANY)

    assert not bs.empty
    assert len(bs) >= 1


def test_tcs_cashflow_available():
    cf = get_cf(TEST_COMPANY)

    assert not cf.empty
    assert len(cf) >= 1


def test_tcs_valuation_available():
    valuation = get_valuation(
        TEST_COMPANY
    )

    assert not valuation.empty
    assert len(valuation) >= 1


def test_tcs_ratio_columns():
    ratios = get_ratios(TEST_COMPANY)

    required = {
        "year",
        "roe_pct",
        "roce_pct",
        "npm_pct",
        "de_ratio",
        "revenue_cagr_5yr",
    }

    assert required.issubset(
        ratios.columns
    )


def test_tcs_pl_columns():
    pl = get_pl(TEST_COMPANY)

    required = {
        "year",
        "sales",
        "net_profit",
        "eps",
    }

    assert required.issubset(
        pl.columns
    )


def test_tcs_valuation_columns():
    valuation = get_valuation(
        TEST_COMPANY
    )

    required = {
        "year",
        "market_cap_crore",
        "pe_ratio",
        "pb_ratio",
        "ev_ebitda",
        "dividend_yield_pct",
    }

    assert required.issubset(
        valuation.columns
    )