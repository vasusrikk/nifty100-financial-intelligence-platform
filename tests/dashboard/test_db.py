"""Sprint 4 - Day 22 dashboard scaffold and database-loader tests."""

from pathlib import Path

import pandas as pd

from src.dashboard.utils.db import (
    DATABASE_PATH,
    get_bs,
    get_cf,
    get_companies,
    get_documents,
    get_market_cap,
    get_peer_groups,
    get_peers,
    get_pl,
    get_ratios,
    get_sectors,
    get_valuation,
)


# ============================================================
# PROJECT / DATABASE
# ============================================================

def test_database_exists():
    assert DATABASE_PATH.exists()


def test_database_is_file():
    assert DATABASE_PATH.is_file()


# ============================================================
# COMPANY MASTER
# ============================================================

def test_get_companies_returns_dataframe():
    result = get_companies()

    assert isinstance(
        result,
        pd.DataFrame,
    )


def test_company_universe_is_92():
    result = get_companies()

    assert len(result) == 92


def test_company_ids_are_unique():
    result = get_companies()

    assert result[
        "company_id"
    ].nunique() == 92


def test_company_required_columns():
    result = get_companies()

    required = {
        "company_id",
        "company_name",
        "broad_sector",
        "sub_sector",
    }

    assert required.issubset(
        result.columns
    )


def test_tcs_exists():
    result = get_companies()

    assert "TCS" in set(
        result["company_id"]
    )


# ============================================================
# RATIOS
# ============================================================

def test_get_ratios_returns_dataframe():
    result = get_ratios(
        "TCS"
    )

    assert isinstance(
        result,
        pd.DataFrame,
    )


def test_tcs_ratios_available():
    result = get_ratios(
        "TCS"
    )

    assert not result.empty


def test_ratio_company_filter():
    result = get_ratios(
        "TCS"
    )

    assert set(
        result["company_id"]
    ) == {"TCS"}


def test_ratio_year_filter():
    all_ratios = get_ratios(
        "TCS"
    )

    year = all_ratios.iloc[0][
        "year"
    ]

    result = get_ratios(
        "TCS",
        year=year,
    )

    assert not result.empty

    assert set(
        result["year"]
    ) == {year}


# ============================================================
# PROFIT AND LOSS
# ============================================================

def test_get_pl_returns_dataframe():
    result = get_pl(
        "TCS"
    )

    assert isinstance(
        result,
        pd.DataFrame,
    )


def test_tcs_pl_available():
    result = get_pl(
        "TCS"
    )

    assert not result.empty


def test_pl_required_columns():
    result = get_pl(
        "TCS"
    )

    required = {
        "company_id",
        "year",
        "sales",
        "net_profit",
        "eps",
    }

    assert required.issubset(
        result.columns
    )


def test_pl_sorted_ascending():
    result = get_pl(
        "TCS"
    )

    years = result[
        "year"
    ].tolist()

    assert years == sorted(
        years
    )


# ============================================================
# BALANCE SHEET
# ============================================================

def test_get_bs_returns_dataframe():
    result = get_bs(
        "TCS"
    )

    assert isinstance(
        result,
        pd.DataFrame,
    )


def test_tcs_balance_sheet_available():
    result = get_bs(
        "TCS"
    )

    assert not result.empty


def test_balance_sheet_required_columns():
    result = get_bs(
        "TCS"
    )

    required = {
        "company_id",
        "year",
        "borrowings",
        "total_liabilities",
        "total_assets",
    }

    assert required.issubset(
        result.columns
    )


# ============================================================
# CASH FLOW
# ============================================================

def test_get_cf_returns_dataframe():
    result = get_cf(
        "TCS"
    )

    assert isinstance(
        result,
        pd.DataFrame,
    )


def test_tcs_cashflow_available():
    result = get_cf(
        "TCS"
    )

    assert not result.empty


def test_cashflow_required_columns():
    result = get_cf(
        "TCS"
    )

    required = {
        "company_id",
        "year",
        "operating_activity",
        "investing_activity",
        "financing_activity",
        "net_cash_flow",
    }

    assert required.issubset(
        result.columns
    )


# ============================================================
# SECTORS
# ============================================================

def test_get_sectors_returns_dataframe():
    result = get_sectors()

    assert isinstance(
        result,
        pd.DataFrame,
    )


def test_sector_company_count_is_92():
    result = get_sectors()

    assert len(result) == 92


def test_sector_company_ids_unique():
    result = get_sectors()

    assert result[
        "company_id"
    ].nunique() == 92


def test_broad_sector_count():
    result = get_sectors()

    assert result[
        "broad_sector"
    ].nunique() == 10


# ============================================================
# PEER ANALYTICS
# ============================================================

def test_peer_groups_count():
    result = get_peer_groups()

    assert len(result) == 11


def test_peer_groups_unique():
    result = get_peer_groups()

    assert len(result) == len(
        set(result)
    )


def test_it_services_peer_rows():
    result = get_peers(
        "IT Services"
    )

    assert len(result) == 75


def test_it_services_has_five_companies():
    result = get_peers(
        "IT Services"
    )

    assert result[
        "company_id"
    ].nunique() == 5


def test_peer_required_columns():
    result = get_peers(
        "IT Services"
    )

    required = {
        "peer_group_name",
        "company_id",
        "company_name",
        "is_benchmark",
        "metric",
        "raw_value",
        "percentile",
    }

    assert required.issubset(
        result.columns
    )


def test_it_services_has_one_benchmark():
    result = get_peers(
        "IT Services"
    )

    benchmarks = result.loc[
        result["is_benchmark"] == 1,
        "company_id",
    ].unique()

    assert len(benchmarks) == 1

    assert benchmarks[0] == "TCS"


# ============================================================
# VALUATION
# ============================================================

def test_get_valuation_returns_dataframe():
    result = get_valuation(
        "TCS"
    )

    assert isinstance(
        result,
        pd.DataFrame,
    )


def test_tcs_valuation_available():
    result = get_valuation(
        "TCS"
    )

    assert not result.empty


def test_valuation_required_columns():
    result = get_valuation(
        "TCS"
    )

    required = {
        "company_id",
        "company_name",
        "broad_sector",
        "year",
        "market_cap_crore",
        "enterprise_value_crore",
        "pe_ratio",
        "pb_ratio",
        "ev_ebitda",
        "dividend_yield_pct",
    }

    assert required.issubset(
        result.columns
    )


# ============================================================
# MARKET CAP
# ============================================================

def test_market_cap_full_data_available():
    result = get_market_cap()

    assert isinstance(
        result,
        pd.DataFrame,
    )

    assert not result.empty


def test_tcs_market_cap_available():
    result = get_market_cap(
        "TCS"
    )

    assert not result.empty

    assert set(
        result["company_id"]
    ) == {"TCS"}


# ============================================================
# DOCUMENTS
# ============================================================

def test_documents_returns_dataframe():
    result = get_documents(
        "TCS"
    )

    assert isinstance(
        result,
        pd.DataFrame,
    )


def test_documents_expected_columns():
    result = get_documents(
        "TCS"
    )

    assert {
        "company_id",
        "year",
        "annual_report",
    }.issubset(
        result.columns
    )


# ============================================================
# DASHBOARD SCAFFOLD
# ============================================================

def test_dashboard_app_exists():
    path = Path(
        "src/dashboard/app.py"
    )

    assert path.exists()


def test_dashboard_pages_directory_exists():
    path = Path(
        "src/dashboard/pages"
    )

    assert path.is_dir()


def test_all_eight_pages_exist():

    pages = [
        "01_home.py",
        "02_profile.py",
        "03_screener.py",
        "04_peers.py",
        "05_trends.py",
        "06_sectors.py",
        "07_capital.py",
        "08_reports.py",
    ]

    directory = Path(
        "src/dashboard/pages"
    )

    for page in pages:
        assert (
            directory / page
        ).exists()


def test_exactly_eight_numbered_pages():

    directory = Path(
        "src/dashboard/pages"
    )

    pages = list(
        directory.glob(
            "[0-9][0-9]_*.py"
        )
    )

    assert len(pages) == 8


# ============================================================
# DAY 22 SOURCE CONFIGURATION
# ============================================================

def test_app_uses_wide_layout():

    source = Path(
        "src/dashboard/app.py"
    ).read_text(
        encoding="utf-8"
    )

    assert 'layout="wide"' in source


def test_app_uses_expanded_sidebar():

    source = Path(
        "src/dashboard/app.py"
    ).read_text(
        encoding="utf-8"
    )

    assert (
        'initial_sidebar_state="expanded"'
        in source
    )


def test_app_has_nifty_title():

    source = Path(
        "src/dashboard/app.py"
    ).read_text(
        encoding="utf-8"
    )

    assert (
        'page_title="Nifty 100 Analytics"'
        in source
    )


def test_db_cache_ttl_is_600():

    source = Path(
        "src/dashboard/utils/db.py"
    ).read_text(
        encoding="utf-8"
    )

    assert "CACHE_TTL = 600" in source


def test_required_db_functions_exist():

    required_functions = [
        get_companies,
        get_ratios,
        get_pl,
        get_bs,
        get_cf,
        get_sectors,
        get_peers,
        get_valuation,
    ]

    assert all(
        callable(function)
        for function
        in required_functions
    )