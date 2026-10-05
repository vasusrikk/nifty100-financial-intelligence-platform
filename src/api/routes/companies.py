"""Sprint 6 - Day 39: Company API endpoints."""

from __future__ import annotations

import sqlite3

from fastapi import APIRouter, HTTPException, Query

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATABASE_PATH = PROJECT_ROOT / "nifty100.db"


router = APIRouter(
    prefix="/api/companies",
    tags=["Companies"],
)


def get_connection():
    """Create SQLite connection returning dictionary-like rows."""

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    return connection


@router.get("")
def list_companies(
    sector: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=100),
):
    """Return the company universe with sector information."""

    query = """
        SELECT
            c.id AS company_id,
            c.company_name,
            c.company_logo,
            c.website,
            s.broad_sector,
            s.sub_sector,
            s.index_weight_pct,
            s.market_cap_category
        FROM companies c
        LEFT JOIN sectors s
            ON s.company_id = c.id
    """

    params = []

    if sector:

        query += """
            WHERE LOWER(s.broad_sector) = LOWER(?)
        """

        params.append(sector)

    query += """
        ORDER BY c.company_name
        LIMIT ?
    """

    params.append(limit)

    with get_connection() as connection:

        rows = connection.execute(
            query,
            params,
        ).fetchall()

    return {
        "count": len(rows),
        "companies": [
            dict(row)
            for row in rows
        ],
    }


@router.get("/{company_id}")
def company_detail(
    company_id: str,
):
    """Return company master information and sector classification."""

    query = """
        SELECT
            c.id AS company_id,
            c.company_name,
            c.company_logo,
            c.chart_link,
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
        WHERE c.id = ?
    """

    with get_connection() as connection:

        row = connection.execute(
            query,
            (company_id.upper(),),
        ).fetchone()

    if row is None:

        raise HTTPException(
            status_code=404,
            detail="Company not found",
        )

    return dict(row)


@router.get("/{company_id}/ratios")
def company_ratios(
    company_id: str,
    year: str = Query(default="2024-03"),
):
    """Return financial ratios for a company and period."""

    query = """
        SELECT
            company_id,
            year,
            npm_pct,
            opm_pct,
            roe_pct,
            roce_pct,
            roa_pct,
            de_ratio,
            leverage_flag,
            icr,
            icr_flag,
            net_debt,
            net_debt_status,
            asset_turnover,
            revenue_cagr_5yr,
            revenue_cagr_5yr_flag,
            pat_cagr_5yr,
            pat_cagr_5yr_flag,
            eps_cagr_5yr,
            eps_cagr_5yr_flag,
            cfo_margin_pct,
            cfo_pat_ratio,
            cfo_pat_flag,
            fcf,
            fcf_margin_pct,
            capex_sales_pct,
            capex_kpi_status
        FROM financial_ratios
        WHERE company_id = ?
          AND year = ?
    """

    with get_connection() as connection:

        row = connection.execute(
            query,
            (
                company_id.upper(),
                year,
            ),
        ).fetchone()

    if row is None:

        raise HTTPException(
            status_code=404,
            detail=(
                "Financial ratios not found "
                "for requested company/year"
            ),
        )

    return dict(row)


@router.get("/{company_id}/valuation")
def company_valuation(
    company_id: str,
    year: str = Query(default="2024-03"),
):
    """Return market-cap and valuation metrics."""

    query = """
        SELECT
            company_id,
            year,
            market_cap_crore,
            enterprise_value_crore,
            pe_ratio,
            pb_ratio,
            ev_ebitda,
            dividend_yield_pct
        FROM market_cap
        WHERE company_id = ?
          AND year = ?
    """

    with get_connection() as connection:

        row = connection.execute(
            query,
            (
                company_id.upper(),
                year,
            ),
        ).fetchone()

    if row is None:

        raise HTTPException(
            status_code=404,
            detail=(
                "Valuation data not found "
                "for requested company/year"
            ),
        )

    return dict(row)


@router.get("/{company_id}/prices")
def company_prices(
    company_id: str,
    limit: int = Query(
        default=30,
        ge=1,
        le=1000,
    ),
):
    """Return most recent available stock-price observations."""

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
        ORDER BY date DESC
        LIMIT ?
    """

    with get_connection() as connection:

        rows = connection.execute(
            query,
            (
                company_id.upper(),
                limit,
            ),
        ).fetchall()

    if not rows:

        raise HTTPException(
            status_code=404,
            detail="Stock-price data not found",
        )

    return {
        "company_id": company_id.upper(),
        "count": len(rows),
        "prices": [
            dict(row)
            for row in rows
        ],
    }


@router.get("/{company_id}/signals")
def company_signals(
    company_id: str,
):
    """Return generated analytical pros/cons signals."""

    query = """
        SELECT
            company_id,
            signal_type,
            rule_id,
            metric,
            period,
            value_pct,
            message
        FROM generated_pros_cons
        WHERE company_id = ?
        ORDER BY signal_type, rule_id
    """

    with get_connection() as connection:

        rows = connection.execute(
            query,
            (company_id.upper(),),
        ).fetchall()

    return {
        "company_id": company_id.upper(),
        "count": len(rows),
        "signals": [
            dict(row)
            for row in rows
        ],
    }