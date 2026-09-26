"""Sprint 3 - Day 15: NIFTY 100 Screener Filter Engine."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any


DB_PATH = Path("nifty100.db")
FINANCIAL_SECTOR = "financials"

SUPPORTED_FILTERS = {
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


# ============================================================
# DATA LOADING
# ============================================================

def load_screener_data(db_path=DB_PATH):
    """
    Load one latest usable financial-ratio row per company.

    Empty newer periods are ignored.
    """

    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row

    query = """
        WITH usable_ratios AS (
            SELECT
                f.*,
                ROW_NUMBER() OVER (
                    PARTITION BY f.company_id
                    ORDER BY f.year DESC
                ) AS rn
            FROM financial_ratios f
            WHERE
                f.roe_pct IS NOT NULL
                OR f.roce_pct IS NOT NULL
                OR f.npm_pct IS NOT NULL
                OR f.opm_pct IS NOT NULL
                OR f.de_ratio IS NOT NULL
                OR f.icr IS NOT NULL
                OR f.asset_turnover IS NOT NULL
                OR f.revenue_cagr_5yr IS NOT NULL
                OR f.pat_cagr_5yr IS NOT NULL
                OR f.eps_cagr_5yr IS NOT NULL
                OR f.cfo_margin_pct IS NOT NULL
        ),

        latest_market_cap AS (
            SELECT
                m.*,
                ROW_NUMBER() OVER (
                    PARTITION BY m.company_id
                    ORDER BY m.year DESC
                ) AS rn
            FROM market_cap m
        )

        SELECT
            f.company_id,
            TRIM(c.company_name) AS company_name,
            f.year,

            TRIM(s.broad_sector) AS broad_sector,
            TRIM(s.sub_sector) AS sub_sector,
            s.index_weight_pct,
            s.market_cap_category,

            f.npm_pct,
            f.opm_pct,
            f.roe_pct,
            f.roce_pct,
            f.roa_pct,

            f.de_ratio,
            f.leverage_flag,

            f.icr,
            f.icr_flag,

            f.asset_turnover,

            f.revenue_cagr_5yr,
            f.revenue_cagr_5yr_flag,

            f.pat_cagr_5yr,
            f.pat_cagr_5yr_flag,

            f.eps_cagr_5yr,
            f.eps_cagr_5yr_flag,

            f.cfo_margin_pct,
            f.cfo_pat_ratio,
            f.cfo_pat_flag,

            f.fcf,
            f.fcf_margin_pct,
            f.capex_sales_pct,
            f.capex_kpi_status,

            p.sales,
            p.net_profit,
            p.eps,
            p.dividend_payout,

            m.year AS market_cap_year,
            m.market_cap_crore,
            m.enterprise_value_crore,
            m.pe_ratio,
            m.pb_ratio,
            m.ev_ebitda,
            m.dividend_yield_pct

        FROM usable_ratios f

        LEFT JOIN companies c
            ON c.id = f.company_id

        LEFT JOIN sectors s
            ON s.company_id = f.company_id

        LEFT JOIN profitandloss p
            ON p.company_id = f.company_id
           AND p.year = f.year

        LEFT JOIN latest_market_cap m
            ON m.company_id = f.company_id
           AND m.rn = 1

        WHERE f.rn = 1

        ORDER BY f.company_id
    """

    try:
        rows = connection.execute(query).fetchall()
        return [dict(row) for row in rows]

    finally:
        connection.close()


# ============================================================
# HELPERS
# ============================================================

def is_financial(row):
    sector = str(
        row.get("broad_sector") or ""
    ).strip().lower()

    return sector == FINANCIAL_SECTOR


def is_debt_free(row):
    flag = str(
        row.get("icr_flag") or ""
    ).strip().upper()

    if flag == "DEBT_FREE":
        return True

    de_ratio = row.get("de_ratio")

    try:
        return (
            de_ratio is not None
            and float(de_ratio) <= 0
        )

    except (TypeError, ValueError):
        return False


def compare_numeric(
    actual,
    operator,
    expected,
):
    """
    Safely compare numeric values.

    Missing numeric values fail the requested filter.
    """

    if actual is None:
        return False

    try:
        actual = float(actual)
        expected = float(expected)

    except (TypeError, ValueError):
        return False

    if operator == ">":
        return actual > expected

    if operator == ">=":
        return actual >= expected

    if operator == "<":
        return actual < expected

    if operator == "<=":
        return actual <= expected

    if operator == "==":
        return actual == expected

    if operator == "!=":
        return actual != expected

    raise ValueError(
        f"Unsupported operator: {operator}"
    )


# ============================================================
# FILTER ENGINE
# ============================================================

def row_passes_filter(
    row,
    metric,
    operator,
    value,
):
    """
    Evaluate one company against one filter.

    Special handling:
    1. Financial-sector companies bypass D/E filtering.
    2. Debt-free companies pass minimum ICR filters.
    """

    if metric not in SUPPORTED_FILTERS:
        raise ValueError(
            f"Unsupported screener metric: {metric}"
        )

    # --------------------------------------------------------
    # FINANCIALS D/E CARVE-OUT
    # --------------------------------------------------------

    if (
        metric == "de_ratio"
        and is_financial(row)
    ):
        return True

    # --------------------------------------------------------
    # DEBT-FREE ICR HANDLING
    # --------------------------------------------------------

    if (
        metric == "icr"
        and operator in {">", ">="}
        and is_debt_free(row)
    ):
        return True

    return compare_numeric(
        row.get(metric),
        operator,
        value,
    )


def apply_filter(
    rows,
    metric,
    operator,
    value,
):
    """Apply one filter to the screener universe."""

    return [
        row
        for row in rows
        if row_passes_filter(
            row,
            metric,
            operator,
            value,
        )
    ]


def apply_filters(
    rows,
    filters,
):
    """Apply multiple screener filters sequentially."""

    result = list(rows)

    for rule in filters:

        metric = rule.get("metric")
        operator = rule.get("operator")
        value = rule.get("value")

        if metric is None:
            raise ValueError(
                "Filter metric is required."
            )

        if operator is None:
            raise ValueError(
                f"Operator missing for {metric}."
            )

        if value is None:
            raise ValueError(
                f"Value missing for {metric}."
            )

        result = apply_filter(
            result,
            str(metric),
            str(operator),
            value,
        )

    return result


# ============================================================
# PUBLIC SCREENER FUNCTION
# ============================================================

def run_screener(
    filters,
    db_path=DB_PATH,
):
    """Load the universe and execute the requested filters."""

    rows = load_screener_data(
        db_path
    )

    return apply_filters(
        rows,
        filters,
    )


# ============================================================
# DAY 15 VALIDATION
# ============================================================

def count_available(
    rows,
    metric,
):
    return sum(
        1
        for row in rows
        if row.get(metric) is not None
    )


def print_day15_summary(rows):

    print(
        "\n=== SPRINT 3 - DAY 15 "
        "FILTER ENGINE CORE ==="
    )

    print(
        "Latest usable company rows:",
        len(rows),
    )

    unique_companies = {
        row["company_id"]
        for row in rows
    }

    print(
        "Unique companies:",
        len(unique_companies),
    )

    print(
        "Duplicate companies:",
        len(rows) - len(unique_companies),
    )

    financial_count = sum(
        1
        for row in rows
        if is_financial(row)
    )

    print(
        "Financial-sector companies:",
        financial_count,
    )

    print(
        "Supported filter metrics:",
        len(SUPPORTED_FILTERS),
    )

    print("\nFilter availability:")

    for metric in sorted(
        SUPPORTED_FILTERS
    ):
        print(
            f"{metric:<24}: "
            f"{count_available(rows, metric)}"
        )

    print("\nSpecial rules:")

    print(
        "Financials D/E carve-out: ENABLED"
    )

    print(
        "Debt-free ICR handling: ENABLED"
    )

    print(
        "Missing numeric values: "
        "FAIL requested filter"
    )

    fcf_available = count_available(
        rows,
        "fcf",
    )

    print("\nSource-data limitations:")

    print(
        "FCF available:",
        fcf_available,
    )

    if fcf_available == 0:
        print(
            "FCF-based screening unavailable: "
            "explicit Capex source unavailable."
        )


# ============================================================
# CLI / SMOKE TEST
# ============================================================

def main():

    rows = load_screener_data()

    print_day15_summary(rows)

    example_filters = [
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
    ]

    screened = apply_filters(
        rows,
        example_filters,
    )

    print(
        "\nSmoke test: ROE > 15 and D/E < 1"
    )

    print(
        "Companies returned:",
        len(screened),
    )

    print(
        "\nFirst 20 results:"
    )

    for row in screened[:20]:

        print(
            row["company_id"],
            "|",
            row["company_name"],
            "|",
            row["year"],
            "|",
            row["broad_sector"],
            "| ROE:",
            round(row["roe_pct"], 2)
            if row["roe_pct"] is not None
            else None,
            "| D/E:",
            round(row["de_ratio"], 2)
            if row["de_ratio"] is not None
            else None,
        )


if __name__ == "__main__":
    main()