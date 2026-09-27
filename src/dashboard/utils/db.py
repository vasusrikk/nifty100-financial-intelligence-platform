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