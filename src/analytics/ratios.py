"""Sprint 2 Financial Ratio Engine.

Day 08:
- Net Profit Margin
- Operating Profit Margin
- ROE
- ROCE
- ROA
- OPM cross-validation
- Financial-sector identification
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Optional

import pandas as pd


DB_PATH = Path("nifty100.db")
OUTPUT_PATH = Path("output/day08_profitability_ratios.csv")


# =========================================================
# DAY 08 - PROFITABILITY FORMULAS
# =========================================================

def net_profit_margin(
    net_profit: float,
    sales: float,
) -> Optional[float]:
    """NPM = Net Profit / Sales * 100."""

    if net_profit is None or sales is None or sales == 0:
        return None

    return (net_profit / sales) * 100


def operating_profit_margin(
    operating_profit: float,
    sales: float,
) -> Optional[float]:
    """OPM = Operating Profit / Sales * 100."""

    if operating_profit is None or sales is None or sales == 0:
        return None

    return (operating_profit / sales) * 100


def validate_opm(
    calculated_opm: Optional[float],
    source_opm: Optional[float],
    tolerance: float = 1.0,
) -> str:
    """Cross-check calculated OPM against source OPM."""

    if calculated_opm is None or source_opm is None:
        return "MISSING"

    difference = abs(calculated_opm - source_opm)

    if difference > tolerance:
        return "MISMATCH"

    return "PASS"


def return_on_equity(
    net_profit: float,
    equity_capital: float,
    reserves: float,
) -> Optional[float]:
    """ROE = Net Profit / Shareholders' Equity * 100."""

    if (
        net_profit is None
        or equity_capital is None
        or reserves is None
    ):
        return None

    equity = equity_capital + reserves

    if equity <= 0:
        return None

    return (net_profit / equity) * 100


def return_on_capital_employed(
    ebit: float,
    equity_capital: float,
    reserves: float,
    borrowings: float,
) -> Optional[float]:
    """ROCE = EBIT / Capital Employed * 100."""

    if (
        ebit is None
        or equity_capital is None
        or reserves is None
        or borrowings is None
    ):
        return None

    capital_employed = (
        equity_capital
        + reserves
        + borrowings
    )

    if capital_employed <= 0:
        return None

    return (ebit / capital_employed) * 100


def return_on_assets(
    net_profit: float,
    total_assets: float,
) -> Optional[float]:
    """ROA = Net Profit / Total Assets * 100."""

    if net_profit is None or total_assets is None:
        return None

    if total_assets == 0:
        return None

    return (net_profit / total_assets) * 100


def is_financial_sector(
    broad_sector: Optional[str],
) -> bool:
    """Return True when company belongs to Financials."""

    if broad_sector is None:
        return False

    return (
        str(broad_sector)
        .strip()
        .lower()
        == "financials"
    )
def roce_benchmark_flag(
    roce: Optional[float],
    broad_sector: Optional[str],
    sector_median_roce: Optional[float] = None,
) -> str:
    """
    Classify ROCE using a sector-relative benchmark for Financials.

    Financial-sector ROCE is compared with the Financials-sector
    median instead of using an absolute ROCE threshold.
    """

    if roce is None:
        return "N/A"

    if is_financial_sector(broad_sector):
        if sector_median_roce is None:
            return "SECTOR_BENCHMARK_UNAVAILABLE"

        if roce >= sector_median_roce:
            return "ABOVE_SECTOR_MEDIAN"

        return "BELOW_SECTOR_MEDIAN"

    return "NOT_APPLICABLE"


# =========================================================
# DATABASE PROFITABILITY ENGINE
# =========================================================

def build_profitability_ratios() -> pd.DataFrame:
    """Calculate Day 08 KPIs using Sprint 1 SQLite data."""

    connection = sqlite3.connect(DB_PATH)

    query = """
    SELECT
        p.company_id,
        p.year,
        p.sales,
        p.operating_profit,
        p.net_profit,
        p.opm_percentage AS source_opm,

        b.equity_capital,
        b.reserves,
        b.borrowings,
        b.total_assets,

        s.broad_sector

    FROM profitandloss AS p

    LEFT JOIN balancesheet AS b
        ON p.company_id = b.company_id
        AND p.year = b.year

    LEFT JOIN sectors AS s
        ON p.company_id = s.company_id

    ORDER BY
        p.company_id,
        p.year
    """

    df = pd.read_sql_query(
        query,
        connection,
    )

    connection.close()

    numeric_columns = [
        "sales",
        "operating_profit",
        "net_profit",
        "source_opm",
        "equity_capital",
        "reserves",
        "borrowings",
        "total_assets",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )

    # NPM
    df["npm_pct"] = df.apply(
        lambda row: net_profit_margin(
            row["net_profit"],
            row["sales"],
        ),
        axis=1,
    )

    # OPM
    df["opm_pct"] = df.apply(
        lambda row: operating_profit_margin(
            row["operating_profit"],
            row["sales"],
        ),
        axis=1,
    )

    # OPM cross-validation
    df["opm_difference_pp"] = (
        df["opm_pct"]
        - df["source_opm"]
    ).abs()

    df["opm_validation"] = df.apply(
        lambda row: validate_opm(
            row["opm_pct"],
            row["source_opm"],
        ),
        axis=1,
    )

    # ROE
    df["roe_pct"] = df.apply(
        lambda row: return_on_equity(
            row["net_profit"],
            row["equity_capital"],
            row["reserves"],
        ),
        axis=1,
    )

    # ROCE
    # operating_profit is used as the available EBIT proxy.
    df["roce_pct"] = df.apply(
        lambda row: return_on_capital_employed(
            row["operating_profit"],
            row["equity_capital"],
            row["reserves"],
            row["borrowings"],
        ),
        axis=1,
    )

    # ROA
    df["roa_pct"] = df.apply(
        lambda row: return_on_assets(
            row["net_profit"],
            row["total_assets"],
        ),
        axis=1,
    )

    # Financial-sector marker
    df["is_financial_sector"] = (
        df["broad_sector"]
        .apply(is_financial_sector)
    )

    output_columns = [
        "company_id",
        "year",
        "broad_sector",
        "npm_pct",
        "opm_pct",
        "roe_pct",
        "roce_pct",
        "roa_pct",
        "source_opm",
        "opm_difference_pp",
        "opm_validation",
        "is_financial_sector",
    ]

    result = df[output_columns].copy()

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    result.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    return result


def print_summary(
    result: pd.DataFrame,
) -> None:
    """Print Day 08 verification results."""

    print(
        "\n=== SPRINT 2 - DAY 08 "
        "PROFITABILITY ENGINE ==="
    )

    print(
        "Rows processed:",
        len(result),
    )

    print("\nKPI availability:")

    print(
        "NPM :",
        result["npm_pct"].notna().sum(),
    )

    print(
        "OPM :",
        result["opm_pct"].notna().sum(),
    )

    print(
        "ROE :",
        result["roe_pct"].notna().sum(),
    )

    print(
        "ROCE:",
        result["roce_pct"].notna().sum(),
    )

    print(
        "ROA :",
        result["roa_pct"].notna().sum(),
    )

    print("\nOPM cross-check:")

    print(
        result["opm_validation"]
        .value_counts(dropna=False)
    )

    print(
        "\nFinancial-sector rows:",
        result["is_financial_sector"].sum(),
    )

    print(
        "\nSaved:",
        OUTPUT_PATH,
    )


if __name__ == "__main__":

    result = build_profitability_ratios()

    print_summary(result)






















# =========================================================
# DAY 09 - LEVERAGE & EFFICIENCY RATIOS
# =========================================================

def debt_to_equity(
    borrowings: float,
    equity_capital: float,
    reserves: float,
) -> Optional[float]:
    """D/E = Borrowings / Shareholders' Equity."""

    if (
        borrowings is None
        or equity_capital is None
        or reserves is None
    ):
        return None

    equity = equity_capital + reserves

    if equity <= 0:
        return None

    if borrowings == 0:
        return 0.0

    return borrowings / equity


def leverage_flag(
    de_ratio: Optional[float],
    broad_sector: Optional[str],
) -> str:
    """
    Flag high leverage.

    Financial-sector companies receive a sector-relative marker
    because conventional D/E thresholds are not directly comparable.
    """

    if de_ratio is None:
        return "N/A"

    if is_financial_sector(broad_sector):
        return "SECTOR_RELATIVE"

    if de_ratio > 5.0:
        return "HIGH_LEVERAGE"

    return "NORMAL"


def interest_coverage_ratio(
    ebit: float,
    interest: float,
) -> Optional[float]:
    """ICR = EBIT / Interest Expense."""

    if ebit is None or interest is None:
        return None

    if interest == 0:
        return None

    return ebit / interest


def interest_coverage_flag(
    icr: Optional[float],
    borrowings: float,
    interest: float,
) -> str:
    """Classify debt-free and weak interest coverage cases."""

    if borrowings is not None and borrowings == 0:
        return "DEBT_FREE"

    if interest is not None and interest == 0:
        return "DEBT_FREE"

    if icr is None:
        return "N/A"

    if icr < 1.5:
        return "ICR_WARNING"

    return "NORMAL"


def net_debt(
    borrowings: float,
    cash_equivalents: float,
) -> Optional[float]:
    """Net Debt = Borrowings - Cash / Cash Equivalents."""

    if borrowings is None or cash_equivalents is None:
        return None

    return borrowings - cash_equivalents


def asset_turnover(
    sales: float,
    total_assets: float,
) -> Optional[float]:
    """Asset Turnover = Sales / Total Assets."""

    if sales is None or total_assets is None:
        return None

    if total_assets == 0:
        return None

    return sales / total_assets










# =========================================================
# DAY 09 - DATABASE LEVERAGE & EFFICIENCY ENGINE
# =========================================================

DAY09_OUTPUT = Path("output/day09_leverage_efficiency.csv")


def build_leverage_efficiency_ratios() -> pd.DataFrame:
    """Calculate Day 09 leverage and efficiency KPIs from SQLite."""

    connection = sqlite3.connect(DB_PATH)

    query = """
    SELECT
        p.company_id,
        p.year,
        p.sales,
        p.operating_profit,
        p.interest,
        b.equity_capital,
        b.reserves,
        b.borrowings,
        b.total_assets,
        s.broad_sector
    FROM profitandloss AS p
    LEFT JOIN balancesheet AS b
        ON p.company_id = b.company_id
        AND p.year = b.year
    LEFT JOIN sectors AS s
        ON p.company_id = s.company_id
    ORDER BY p.company_id, p.year
    """

    df = pd.read_sql_query(query, connection)
    connection.close()

    numeric_columns = [
        "sales",
        "operating_profit",
        "interest",
        "equity_capital",
        "reserves",
        "borrowings",
        "total_assets",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )

    # Debt-to-Equity
    df["de_ratio"] = df.apply(
        lambda row: debt_to_equity(
            row["borrowings"],
            row["equity_capital"],
            row["reserves"],
        ),
        axis=1,
    )

    df["leverage_flag"] = df.apply(
        lambda row: leverage_flag(
            row["de_ratio"],
            row["broad_sector"],
        ),
        axis=1,
    )

    # Interest Coverage Ratio
    # operating_profit is used as the available EBIT proxy.
    df["icr"] = df.apply(
        lambda row: interest_coverage_ratio(
            row["operating_profit"],
            row["interest"],
        ),
        axis=1,
    )

    df["icr_flag"] = df.apply(
        lambda row: interest_coverage_flag(
            row["icr"],
            row["borrowings"],
            row["interest"],
        ),
        axis=1,
    )

    # Net Debt cannot be populated because the supplied
    # balance-sheet dataset has no cash/cash-equivalents field.
    df["net_debt"] = pd.NA
    df["net_debt_status"] = "SOURCE_CASH_FIELD_UNAVAILABLE"

    # Asset Turnover
    df["asset_turnover"] = df.apply(
        lambda row: asset_turnover(
            row["sales"],
            row["total_assets"],
        ),
        axis=1,
    )

    output_columns = [
        "company_id",
        "year",
        "broad_sector",
        "de_ratio",
        "leverage_flag",
        "icr",
        "icr_flag",
        "net_debt",
        "net_debt_status",
        "asset_turnover",
    ]

    result = df[output_columns].copy()

    DAY09_OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    result.to_csv(
        DAY09_OUTPUT,
        index=False,
    )

    return result


def print_day09_summary(result: pd.DataFrame) -> None:
    """Print Day 09 verification summary."""

    print(
        "\n=== SPRINT 2 - DAY 09 "
        "LEVERAGE & EFFICIENCY ENGINE ==="
    )

    print("Rows processed:", len(result))

    print("\nKPI availability:")
    print("D/E           :", result["de_ratio"].notna().sum())
    print("ICR           :", result["icr"].notna().sum())
    print("Net Debt      :", result["net_debt"].notna().sum())
    print(
        "Asset Turnover:",
        result["asset_turnover"].notna().sum(),
    )

    print("\nLeverage flags:")
    print(
        result["leverage_flag"]
        .value_counts(dropna=False)
    )

    print("\nICR flags:")
    print(
        result["icr_flag"]
        .value_counts(dropna=False)
    )

    print(
        "\nNet Debt status:",
        result["net_debt_status"].iloc[0],
    )

    print("\nSaved:", DAY09_OUTPUT)


if __name__ == "__main__":
    day09_result = build_leverage_efficiency_ratios()
    print_day09_summary(day09_result)


