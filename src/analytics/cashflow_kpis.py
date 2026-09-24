"""Sprint 2 - Day 11 Cash Flow KPI Engine.

Calculates:
- CFO Margin
- CFO / PAT
- Free Cash Flow (when Capex source is available)
- FCF Margin
- Capex / Sales
- Capital-allocation evidence

Important:
The supplied Sprint 1 database does not contain an explicit Capex
field. Investing activity is not assumed to equal Capex.
"""

from pathlib import Path
from typing import Optional

import pandas as pd
import sqlite3


# =========================================================
# PATHS / CONSTANTS
# =========================================================

DB_PATH = Path("nifty100.db")

DAY11_OUTPUT = Path(
    "output/day11_cashflow_kpis.csv"
)

CAPITAL_ALLOCATION_OUTPUT = Path(
    "output/capital_allocation.csv"
)

CAPEX_SOURCE_UNAVAILABLE = (
    "CAPEX_SOURCE_UNAVAILABLE"
)
NORMAL = "NORMAL"
ZERO_PAT = "ZERO_PAT"
NEGATIVE_PAT = "NEGATIVE_PAT"
MISSING = "MISSING"

# =========================================================
# DAY 11 - CASH FLOW KPI FORMULAS
# =========================================================

def cfo_margin(
    operating_cash_flow: float,
    sales: float,
) -> Optional[float]:
    """CFO Margin = CFO / Sales * 100."""

    if (
        operating_cash_flow is None
        or sales is None
        or pd.isna(operating_cash_flow)
        or pd.isna(sales)
        or sales == 0
    ):
        return None

    return (
        operating_cash_flow
        / sales
    ) * 100


def cfo_to_pat(
    operating_cash_flow: float,
    net_profit: float,
) -> Optional[float]:
    """CFO/PAT = Operating Cash Flow / Net Profit."""

    if (
        operating_cash_flow is None
        or net_profit is None
        or pd.isna(operating_cash_flow)
        or pd.isna(net_profit)
        or net_profit == 0
    ):
        return None

    return (
        operating_cash_flow
        / net_profit
    )


def cfo_pat_classification(
    operating_cash_flow: float,
    net_profit: float,
) -> str:
    """Classify CFO/PAT edge cases."""

    if (
        operating_cash_flow is None
        or net_profit is None
        or pd.isna(operating_cash_flow)
        or pd.isna(net_profit)
    ):
        return MISSING

    if net_profit == 0:
        return ZERO_PAT

    if net_profit < 0:
        return NEGATIVE_PAT

    return NORMAL




def cfo_to_pat_flag(
    operating_cash_flow: float,
    net_profit: float,
) -> str:
    """Backward-compatible CFO/PAT classification helper."""

    return cfo_pat_classification(
        operating_cash_flow,
        net_profit,
    )

def free_cash_flow(
    operating_cash_flow: float,
    capex: float,
) -> Optional[float]:
    """FCF = Operating Cash Flow - Capex."""

    if (
        operating_cash_flow is None
        or capex is None
        or pd.isna(operating_cash_flow)
        or pd.isna(capex)
    ):
        return None

    return (
        operating_cash_flow
        - capex
    )


def fcf_margin(
    fcf: float,
    sales: float,
) -> Optional[float]:
    """FCF Margin = FCF / Sales * 100."""

    if (
        fcf is None
        or sales is None
        or pd.isna(fcf)
        or pd.isna(sales)
        or sales == 0
    ):
        return None

    return (
        fcf
        / sales
    ) * 100


def capex_to_sales(
    capex: float,
    sales: float,
) -> Optional[float]:
    """Capex / Sales = Capex / Sales * 100."""

    if (
        capex is None
        or sales is None
        or pd.isna(capex)
        or pd.isna(sales)
        or sales == 0
    ):
        return None

    return (
        capex
        / sales
    ) * 100


# =========================================================
# DATABASE CASH FLOW KPI ENGINE
# =========================================================

def build_cashflow_kpis() -> pd.DataFrame:
    """Calculate Sprint 2 Day 11 cash-flow KPIs."""

    connection = sqlite3.connect(DB_PATH)

    query = """
        SELECT
            cf.company_id,
            cf.year,
            cf.operating_activity,
            cf.investing_activity,
            cf.financing_activity,
            cf.net_cash_flow,
            p.sales,
            p.net_profit
        FROM cashflow cf
        LEFT JOIN profitandloss p
            ON cf.company_id = p.company_id
            AND cf.year = p.year
        ORDER BY
            cf.company_id,
            cf.year
    """

    df = pd.read_sql_query(
        query,
        connection,
    )

    connection.close()

    # -----------------------------------------------------
    # CFO MARGIN
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
        lambda row: cfo_pat_classification(
            row["operating_activity"],
            row["net_profit"],
        ),
        axis=1,
    )

    # -----------------------------------------------------
    # CAPEX-DEPENDENT KPIs
    # -----------------------------------------------------
    #
    # The supplied database contains:
    #
    # cashflow:
    #   operating_activity
    #   investing_activity
    #   financing_activity
    #   net_cash_flow
    #
    # balancesheet:
    #   fixed_assets
    #   cwip
    #
    # There is NO explicit Capex field.
    #
    # Investing activity must NOT automatically be treated
    # as Capex because it can include acquisitions,
    # investments, disposals and other investing cash flows.
    #
    # Therefore FCF, FCF Margin and Capex/Sales remain
    # unavailable instead of being fabricated.
    # -----------------------------------------------------

    df["fcf"] = pd.NA
    df["fcf_margin_pct"] = pd.NA
    df["capex_sales_pct"] = pd.NA

    df["capex_kpi_status"] = (
        CAPEX_SOURCE_UNAVAILABLE
    )

    # -----------------------------------------------------
    # DAY 11 KPI OUTPUT
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

    result = df[
        output_columns
    ].copy()

    DAY11_OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    result.to_csv(
        DAY11_OUTPUT,
        index=False,
    )

    # -----------------------------------------------------
    # CAPITAL ALLOCATION OUTPUT
    # -----------------------------------------------------
    #
    # Sprint 2 requires:
    # output/capital_allocation.csv
    #
    # Because explicit Capex is unavailable, the file
    # records the available cash-flow evidence together
    # with an explicit source-unavailable status.
    # -----------------------------------------------------

    capital_allocation_columns = [
        "company_id",
        "year",
        "operating_activity",
        "investing_activity",
        "financing_activity",
        "net_cash_flow",
        "sales",
        "net_profit",
        "fcf",
        "fcf_margin_pct",
        "capex_sales_pct",
        "capex_kpi_status",
    ]

    capital_allocation = df[
        capital_allocation_columns
    ].copy()

    capital_allocation.to_csv(
        CAPITAL_ALLOCATION_OUTPUT,
        index=False,
    )

    return result


# =========================================================
# DAY 11 QA SUMMARY
# =========================================================

def print_day11_summary(
    result: pd.DataFrame,
) -> None:
    """Print Day 11 QA summary."""

    print(
        "\n=== SPRINT 2 - DAY 11 "
        "CASH FLOW KPI ENGINE ==="
    )

    print(
        "Rows processed:",
        len(result),
    )

    print(
        "\nKPI availability:"
    )

    print(
        "CFO Margin :",
        result[
            "cfo_margin_pct"
        ].notna().sum(),
    )

    print(
        "CFO/PAT    :",
        result[
            "cfo_pat_ratio"
        ].notna().sum(),
    )

    print(
        "FCF        :",
        result[
            "fcf"
        ].notna().sum(),
    )

    print(
        "FCF Margin :",
        result[
            "fcf_margin_pct"
        ].notna().sum(),
    )

    print(
        "Capex/Sales:",
        result[
            "capex_sales_pct"
        ].notna().sum(),
    )

    print(
        "\nCFO/PAT flags:"
    )

    print(
        result[
            "cfo_pat_flag"
        ].value_counts(
            dropna=False
        )
    )

    print(
        "\nCapex-dependent KPI status:",
        CAPEX_SOURCE_UNAVAILABLE,
    )

    print(
        "\nSaved:",
        DAY11_OUTPUT,
    )

    print(
        "Saved:",
        CAPITAL_ALLOCATION_OUTPUT,
    )


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":
    result = build_cashflow_kpis()
    print_day11_summary(result)