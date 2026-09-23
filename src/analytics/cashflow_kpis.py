"""Sprint 2 - Day 11 Cash Flow KPI Engine.

KPIs:
- CFO Margin
- CFO / PAT
- FCF
- FCF Margin
- Capex / Sales

The supplied source dataset does not contain an explicit
Capex field. Capex-dependent KPIs are therefore marked
unavailable rather than estimated from investing_activity.
"""

from __future__ import annotations

from typing import Optional


CAPEX_SOURCE_UNAVAILABLE = "CAPEX_SOURCE_UNAVAILABLE"
NORMAL = "NORMAL"
ZERO_SALES = "ZERO_SALES"
ZERO_PAT = "ZERO_PAT"
NEGATIVE_PAT = "NEGATIVE_PAT"
MISSING = "MISSING"


# =========================================================
# CFO MARGIN
# =========================================================

def cfo_margin(
    operating_activity: Optional[float],
    sales: Optional[float],
) -> Optional[float]:
    """CFO Margin = CFO / Sales * 100."""

    if operating_activity is None or sales is None:
        return None

    if sales == 0:
        return None

    return (operating_activity / sales) * 100


# =========================================================
# CFO / PAT
# =========================================================

def cfo_to_pat(
    operating_activity: Optional[float],
    net_profit: Optional[float],
) -> Optional[float]:
    """CFO/PAT = Cash Flow from Operations / Net Profit."""

    if operating_activity is None or net_profit is None:
        return None

    if net_profit == 0:
        return None

    return operating_activity / net_profit


def cfo_to_pat_flag(
    operating_activity: Optional[float],
    net_profit: Optional[float],
) -> str:
    """Classify CFO/PAT edge cases."""

    if operating_activity is None or net_profit is None:
        return MISSING

    if net_profit == 0:
        return ZERO_PAT

    if net_profit < 0:
        return NEGATIVE_PAT

    return NORMAL


# =========================================================
# FREE CASH FLOW
# =========================================================

def free_cash_flow(
    operating_activity: Optional[float],
    capex: Optional[float],
) -> Optional[float]:
    """FCF = CFO - Capex."""

    if operating_activity is None or capex is None:
        return None

    return operating_activity - capex


def fcf_margin(
    fcf: Optional[float],
    sales: Optional[float],
) -> Optional[float]:
    """FCF Margin = FCF / Sales * 100."""

    if fcf is None or sales is None:
        return None

    if sales == 0:
        return None

    return (fcf / sales) * 100


# =========================================================
# CAPEX / SALES
# =========================================================

def capex_to_sales(
    capex: Optional[float],
    sales: Optional[float],
) -> Optional[float]:
    """Capex/Sales = Capex / Sales * 100."""

    if capex is None or sales is None:
        return None

    if sales == 0:
        return None

    return (capex / sales) * 100












# =========================================================
# DAY 11 - DATABASE CASH FLOW KPI ENGINE
# =========================================================

import sqlite3
from pathlib import Path

import pandas as pd


DB_PATH = Path("nifty100.db")
DAY11_OUTPUT = Path("output/day11_cashflow_kpis.csv")


def build_cashflow_kpis() -> pd.DataFrame:
    """Calculate Day 11 cash-flow KPIs from SQLite."""

    connection = sqlite3.connect(DB_PATH)

    query = """
    SELECT
        c.company_id,
        c.year,
        c.operating_activity,
        c.investing_activity,
        c.financing_activity,
        c.net_cash_flow,
        p.sales,
        p.net_profit

    FROM cashflow AS c

    LEFT JOIN profitandloss AS p
        ON c.company_id = p.company_id
        AND c.year = p.year

    ORDER BY
        c.company_id,
        c.year
    """

    df = pd.read_sql_query(query, connection)
    connection.close()

    numeric_columns = [
        "operating_activity",
        "investing_activity",
        "financing_activity",
        "net_cash_flow",
        "sales",
        "net_profit",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )

    # -----------------------------------------------------
    # CFO Margin
    # -----------------------------------------------------

    df["cfo_margin_pct"] = df.apply(
        lambda row: cfo_margin(
            row["operating_activity"],
            row["sales"],
        ),
        axis=1,
    )

    # -----------------------------------------------------
    # CFO / PAT
    # -----------------------------------------------------

    df["cfo_pat_ratio"] = df.apply(
        lambda row: cfo_to_pat(
            row["operating_activity"],
            row["net_profit"],
        ),
        axis=1,
    )

    df["cfo_pat_flag"] = df.apply(
        lambda row: cfo_to_pat_flag(
            row["operating_activity"],
            row["net_profit"],
        ),
        axis=1,
    )

    # -----------------------------------------------------
    # CAPEX-DEPENDENT KPIs
    # -----------------------------------------------------
    # The supplied source contains no explicit Capex field.
    # investing_activity is NOT assumed to equal Capex.

    df["fcf"] = pd.NA
    df["fcf_margin_pct"] = pd.NA
    df["capex_sales_pct"] = pd.NA

    df["capex_kpi_status"] = CAPEX_SOURCE_UNAVAILABLE

    # -----------------------------------------------------
    # OUTPUT
    # -----------------------------------------------------

    output_columns = [
        "company_id",
        "year",
        "operating_activity",
        "sales",
        "net_profit",
        "cfo_margin_pct",
        "cfo_pat_ratio",
        "cfo_pat_flag",
        "fcf",
        "fcf_margin_pct",
        "capex_sales_pct",
        "capex_kpi_status",
    ]

    result = df[output_columns].copy()

    DAY11_OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    result.to_csv(
        DAY11_OUTPUT,
        index=False,
    )

    return result


def print_day11_summary(result: pd.DataFrame) -> None:
    """Print Day 11 QA summary."""

    print(
        "\n=== SPRINT 2 - DAY 11 "
        "CASH FLOW KPI ENGINE ==="
    )

    print("Rows processed:", len(result))

    print("\nKPI availability:")

    print(
        "CFO Margin :",
        result["cfo_margin_pct"].notna().sum(),
    )

    print(
        "CFO/PAT    :",
        result["cfo_pat_ratio"].notna().sum(),
    )

    print(
        "FCF        :",
        result["fcf"].notna().sum(),
    )

    print(
        "FCF Margin :",
        result["fcf_margin_pct"].notna().sum(),
    )

    print(
        "Capex/Sales:",
        result["capex_sales_pct"].notna().sum(),
    )

    print("\nCFO/PAT flags:")

    print(
        result["cfo_pat_flag"]
        .value_counts(dropna=False)
    )

    print(
        "\nCapex-dependent KPI status:",
        CAPEX_SOURCE_UNAVAILABLE,
    )

    print("\nSaved:", DAY11_OUTPUT)


if __name__ == "__main__":
    result = build_cashflow_kpis()
    print_day11_summary(result)