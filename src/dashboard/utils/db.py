"""Shared cached SQLite data loader for the Streamlit dashboard."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATABASE_PATH = PROJECT_ROOT / "nifty100.db"

CACHE_TTL = 600


def _connect():
    """
    Create a read-only-style SQLite connection.

    The dashboard uses this connection only for SELECT queries.
    """
    return sqlite3.connect(DATABASE_PATH)


# ============================================================
# COMPANIES
# ============================================================

@st.cache_data(ttl=CACHE_TTL)
def get_companies():
    """
    Return the complete company master with sector information.
    """

    query = """
        SELECT
            c.id AS company_id,
            c.company_name,
            c.company_logo,
            c.about_company,
            c.website,
            c.nse_profile,
            c.bse_profile,
            c.face_value,
            c.book_value,
            c.roce_percentage,
            c.roe_percentage,
            s.broad_sector,
            s.sub_sector,
            s.index_weight_pct,
            s.market_cap_category
        FROM companies c
        LEFT JOIN sectors s
            ON s.company_id = c.id
        ORDER BY c.company_name
    """

    with _connect() as connection:
        return pd.read_sql_query(
            query,
            connection,
        )


# ============================================================
# FINANCIAL RATIOS
# ============================================================

@st.cache_data(ttl=CACHE_TTL)
def get_ratios(
    ticker,
    year=None,
):
    """
    Return financial ratios for one company.

    When year is supplied, only that financial year is returned.
    Otherwise all available years are returned newest first.
    """

    if year is None:

        query = """
            SELECT *
            FROM financial_ratios
            WHERE company_id = ?
            ORDER BY year DESC
        """

        params = (ticker,)

    else:

        query = """
            SELECT *
            FROM financial_ratios
            WHERE company_id = ?
              AND year = ?
            ORDER BY year DESC
        """

        params = (
            ticker,
            year,
        )

    with _connect() as connection:
        return pd.read_sql_query(
            query,
            connection,
            params=params,
        )


# ============================================================
# PROFIT & LOSS
# ============================================================

@st.cache_data(ttl=CACHE_TTL)
def get_pl(ticker):
    """
    Return complete Profit & Loss history for a company.
    """

    query = """
        SELECT *
        FROM profitandloss
        WHERE company_id = ?
        ORDER BY year ASC
    """

    with _connect() as connection:
        return pd.read_sql_query(
            query,
            connection,
            params=(ticker,),
        )


# ============================================================
# BALANCE SHEET
# ============================================================

@st.cache_data(ttl=CACHE_TTL)
def get_bs(ticker):
    """
    Return complete Balance Sheet history for a company.
    """

    query = """
        SELECT *
        FROM balancesheet
        WHERE company_id = ?
        ORDER BY year ASC
    """

    with _connect() as connection:
        return pd.read_sql_query(
            query,
            connection,
            params=(ticker,),
        )


# ============================================================
# CASH FLOW
# ============================================================

@st.cache_data(ttl=CACHE_TTL)
def get_cf(ticker):
    """
    Return complete Cash Flow history for a company.
    """

    query = """
        SELECT *
        FROM cashflow
        WHERE company_id = ?
        ORDER BY year ASC
    """

    with _connect() as connection:
        return pd.read_sql_query(
            query,
            connection,
            params=(ticker,),
        )


# ============================================================
# SECTORS
# ============================================================

@st.cache_data(ttl=CACHE_TTL)
def get_sectors():
    """
    Return sector classification for the full company universe.
    """

    query = """
        SELECT
            s.company_id,
            c.company_name,
            s.broad_sector,
            s.sub_sector,
            s.index_weight_pct,
            s.market_cap_category
        FROM sectors s
        LEFT JOIN companies c
            ON c.id = s.company_id
        ORDER BY
            s.broad_sector,
            s.sub_sector,
            c.company_name
    """

    with _connect() as connection:
        return pd.read_sql_query(
            query,
            connection,
        )


# ============================================================
# PEER ANALYTICS
# ============================================================

@st.cache_data(ttl=CACHE_TTL)
def get_peers(group_name):
    """
    Return peer-percentile records for one peer group.
    """

    query = """
        SELECT
            pp.peer_group_name,
            pp.company_id,
            c.company_name,
            pp.is_benchmark,
            pp.year,
            pp.metric,
            pp.raw_value,
            pp.percentile
        FROM peer_percentiles pp
        LEFT JOIN companies c
            ON c.id = pp.company_id
        WHERE pp.peer_group_name = ?
        ORDER BY
            pp.is_benchmark DESC,
            c.company_name,
            pp.metric
    """

    with _connect() as connection:
        return pd.read_sql_query(
            query,
            connection,
            params=(group_name,),
        )


# ============================================================
# VALUATION
# ============================================================

@st.cache_data(ttl=CACHE_TTL)
def get_valuation(ticker):
    """
    Return available valuation history for a company.

    Day 22 uses the existing market_cap table.
    Day 26 will add derived valuation analytics.
    """

    query = """
        SELECT
            m.company_id,
            c.company_name,
            s.broad_sector,
            s.sub_sector,
            m.year,
            m.market_cap_crore,
            m.enterprise_value_crore,
            m.pe_ratio,
            m.pb_ratio,
            m.ev_ebitda,
            m.dividend_yield_pct
        FROM market_cap m
        LEFT JOIN companies c
            ON c.id = m.company_id
        LEFT JOIN sectors s
            ON s.company_id = m.company_id
        WHERE m.company_id = ?
        ORDER BY m.year DESC
    """

    with _connect() as connection:
        return pd.read_sql_query(
            query,
            connection,
            params=(ticker,),
        )


# ============================================================
# ADDITIONAL DASHBOARD HELPERS
# ============================================================

@st.cache_data(ttl=CACHE_TTL)
def get_peer_groups():
    """
    Return the available peer-group names.
    """

    query = """
        SELECT DISTINCT
            peer_group_name
        FROM peer_percentiles
        WHERE peer_group_name IS NOT NULL
        ORDER BY peer_group_name
    """

    with _connect() as connection:
        frame = pd.read_sql_query(
            query,
            connection,
        )

    return frame[
        "peer_group_name"
    ].tolist()


@st.cache_data(ttl=CACHE_TTL)
def get_market_cap(
    ticker=None,
):
    """
    Return market-cap and valuation data.

    If ticker is None, return the complete dataset.
    """

    if ticker is None:

        query = """
            SELECT *
            FROM market_cap
            ORDER BY company_id, year DESC
        """

        params = None

    else:

        query = """
            SELECT *
            FROM market_cap
            WHERE company_id = ?
            ORDER BY year DESC
        """

        params = (ticker,)

    with _connect() as connection:
        return pd.read_sql_query(
            query,
            connection,
            params=params,
        )


@st.cache_data(ttl=CACHE_TTL)
def get_documents(ticker):
    """
    Return available annual-report records for a company.
    """

    query = """
        SELECT
            company_id,
            Year AS year,
            Annual_Report AS annual_report
        FROM documents
        WHERE company_id = ?
        ORDER BY Year DESC
    """

    with _connect() as connection:
        return pd.read_sql_query(
            query,
            connection,
            params=(ticker,),
        )





# ============================================================
# HOME DASHBOARD
# ============================================================

@st.cache_data(ttl=CACHE_TTL)
def get_available_ratio_years():
    """
    Return available financial-ratio periods with company coverage.
    """

    query = """
        SELECT
            year,
            COUNT(DISTINCT company_id) AS company_count
        FROM financial_ratios
        WHERE year IS NOT NULL
        GROUP BY year
        ORDER BY year DESC
    """

    with _connect() as connection:
        return pd.read_sql_query(
            query,
            connection,
        )


@st.cache_data(ttl=CACHE_TTL)
def get_home_snapshot(year="2024-03"):
    """
    Return one company-level financial snapshot for the Home page.

    Companies remain in the universe even when a particular KPI is
    unavailable. Missing source values remain NULL.
    """

    query = """
        SELECT
            c.id AS company_id,
            c.company_name,
            s.broad_sector,
            s.sub_sector,
            s.index_weight_pct,
            s.market_cap_category,

            fr.year AS ratio_year,
            fr.roe_pct,
            fr.roce_pct,
            fr.npm_pct,
            fr.de_ratio,
            fr.icr,
            fr.revenue_cagr_5yr,
            fr.pat_cagr_5yr,
            fr.cfo_margin_pct,
            fr.fcf,
            fr.fcf_margin_pct,

            mc.market_cap_crore,
            mc.enterprise_value_crore,
            mc.pe_ratio,
            mc.pb_ratio,
            mc.ev_ebitda,
            mc.dividend_yield_pct

        FROM companies c

        LEFT JOIN sectors s
            ON s.company_id = c.id

        LEFT JOIN financial_ratios fr
            ON fr.company_id = c.id
           AND fr.year = ?

        LEFT JOIN market_cap mc
            ON mc.company_id = c.id
           AND mc.year = ?

        ORDER BY c.company_name
    """

    with _connect() as connection:
        return pd.read_sql_query(
            query,
            connection,
            params=(
                year,
                year,
            ),
        )


@st.cache_data(ttl=CACHE_TTL)
def get_home_summary(year="2024-03"):
    """
    Return the six Home-screen KPIs required by Sprint 4.

    Missing source values are excluded from statistical calculations.
    Total company count always represents the complete company universe.
    """

    snapshot = get_home_snapshot(year)

    if snapshot.empty:
        return {
            "average_roe": None,
            "median_pe": None,
            "median_de": None,
            "total_companies": 0,
            "median_revenue_cagr_5yr": None,
            "debt_free_companies": 0,
            "ratio_coverage": 0,
            "market_cap_coverage": 0,
        }

    def safe_mean(column):
        values = snapshot[column].dropna()

        if values.empty:
            return None

        return float(values.mean())

    def safe_median(column):
        values = snapshot[column].dropna()

        if values.empty:
            return None

        return float(values.median())

    de_values = snapshot["de_ratio"].dropna()

    debt_free_companies = int(
        (de_values == 0).sum()
    )

    return {
        "average_roe":
            safe_mean("roe_pct"),

        "median_pe":
            safe_median("pe_ratio"),

        "median_de":
            safe_median("de_ratio"),

        "total_companies":
            int(snapshot["company_id"].nunique()),

        "median_revenue_cagr_5yr":
            safe_median("revenue_cagr_5yr"),

        "debt_free_companies":
            debt_free_companies,

        "ratio_coverage":
            int(snapshot["ratio_year"].notna().sum()),

        "market_cap_coverage":
            int(snapshot["market_cap_crore"].notna().sum()),
    }


    def safe_median(column):
        values = snapshot[
            column
        ].dropna()

        if values.empty:
            return None

        return float(
            values.median()
        )

    return {
        "companies":
            int(
                snapshot[
                    "company_id"
                ].nunique()
            ),
        "sectors":
            int(
                snapshot[
                    "broad_sector"
                ].nunique()
            ),
        "ratio_coverage":
            ratio_coverage,
        "market_cap_coverage":
            market_cap_coverage,
        "median_roe":
            safe_median(
                "roe_pct"
            ),
        "median_roce":
            safe_median(
                "roce_pct"
            ),
        "median_de":
            safe_median(
                "de_ratio"
            ),
        "median_revenue_growth":
            safe_median(
                "revenue_cagr_5yr"
            ),
    }





















































# ============================================================
# STOCK PRICE HISTORY
# ============================================================

@st.cache_data(ttl=CACHE_TTL)
def get_stock_prices(company_id):
    """
    Return historical stock-price data for one company.

    Data is ordered chronologically and source values are
    returned without fabrication or interpolation.
    """

    query = """
        SELECT
            company_id,
            date,
            open_price,
            high_price,
            low_price,
            close_price,
            volume,
            adjusted_close
        FROM stock_prices
        WHERE company_id = ?
        ORDER BY date
    """

    with _connect() as connection:
        return pd.read_sql_query(
            query,
            connection,
            params=(company_id,),
        )