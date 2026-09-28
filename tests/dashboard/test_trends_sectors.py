"""Sprint 4 - Day 25 tests for Trends and Sector Analytics."""

from src.dashboard.utils.db import (
    get_companies,
    get_home_snapshot,
    get_sectors,
    get_stock_prices,
)


YEAR = "2024-03"
TEST_COMPANY = "TCS"


# ============================================================
# TRENDS TESTS
# ============================================================

def test_stock_price_company_coverage():
    companies = get_companies()

    covered = 0

    for company_id in companies["company_id"]:
        prices = get_stock_prices(company_id)

        if not prices.empty:
            covered += 1

    assert covered == 92


def test_tcs_stock_price_rows():
    prices = get_stock_prices(
        TEST_COMPANY
    )

    assert len(prices) == 60


def test_tcs_stock_price_date_range():
    prices = get_stock_prices(
        TEST_COMPANY
    )

    assert prices.iloc[0]["date"] == "2020-01-01"
    assert prices.iloc[-1]["date"] == "2024-12-01"


def test_stock_price_required_columns():
    prices = get_stock_prices(
        TEST_COMPANY
    )

    required = {
        "company_id",
        "date",
        "open_price",
        "high_price",
        "low_price",
        "close_price",
        "volume",
        "adjusted_close",
    }

    assert required.issubset(
        prices.columns
    )


def test_tcs_stock_prices_chronological():
    prices = get_stock_prices(
        TEST_COMPANY
    )

    dates = prices["date"].tolist()

    assert dates == sorted(dates)


# ============================================================
# SECTOR TESTS
# ============================================================

def test_sector_company_coverage():
    sectors = get_sectors()

    assert sectors["company_id"].nunique() == 92


def test_broad_sector_count():
    sectors = get_sectors()

    assert sectors["broad_sector"].nunique() == 10


def test_expected_broad_sectors():
    sectors = get_sectors()

    expected = {
        "Financials",
        "Consumer Discretionary",
        "Energy",
        "Industrials",
        "Materials",
        "Consumer Staples",
        "Healthcare",
        "Information Technology",
        "Communication Services",
        "Real Estate",
    }

    actual = set(
        sectors["broad_sector"]
        .dropna()
        .unique()
    )

    assert actual == expected


def test_financials_company_count():
    sectors = get_sectors()

    count = (
        sectors.loc[
            sectors["broad_sector"]
            == "Financials",
            "company_id",
        ]
        .nunique()
    )

    assert count == 23


def test_communication_services_count():
    sectors = get_sectors()

    count = (
        sectors.loc[
            sectors["broad_sector"]
            == "Communication Services",
            "company_id",
        ]
        .nunique()
    )

    assert count == 2


def test_sector_distribution_totals_92():
    sectors = get_sectors()

    distribution = (
        sectors.groupby(
            "broad_sector"
        )["company_id"]
        .nunique()
    )

    assert distribution.sum() == 92


def test_sector_snapshot_coverage():
    snapshot = get_home_snapshot(
        YEAR
    )

    assert len(snapshot) == 92

    assert (
        snapshot["broad_sector"]
        .notna()
        .sum()
        == 92
    )


def test_sector_snapshot_has_financial_metrics():
    snapshot = get_home_snapshot(
        YEAR
    )

    required = {
        "roe_pct",
        "roce_pct",
        "de_ratio",
        "revenue_cagr_5yr",
        "pe_ratio",
        "pb_ratio",
        "market_cap_crore",
    }

    assert required.issubset(
        snapshot.columns
    )