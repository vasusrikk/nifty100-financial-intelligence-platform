"""Sprint 2 - Day 10 CAGR Engine.

Handles CAGR calculations and required financial edge cases.
"""

from __future__ import annotations

from typing import Optional, Tuple


# =========================================================
# CAGR FLAGS
# =========================================================

NORMAL = "NORMAL"
DECLINE_TO_LOSS = "DECLINE_TO_LOSS"
TURNAROUND = "TURNAROUND"
BOTH_NEGATIVE = "BOTH_NEGATIVE"
ZERO_BASE = "ZERO_BASE"
INSUFFICIENT = "INSUFFICIENT"


# =========================================================
# CORE CAGR CALCULATION
# =========================================================

def calculate_cagr(
    start_value: Optional[float],
    end_value: Optional[float],
    years: int,
) -> Tuple[Optional[float], str]:
    """
    Calculate CAGR and return:

        (cagr_percentage, flag)

    Formula:
        ((end / start) ** (1 / years) - 1) * 100
    """

    # Missing values / insufficient history
    if start_value is None or end_value is None:
        return None, INSUFFICIENT

    if years <= 0:
        return None, INSUFFICIENT

    # Zero starting value
    if start_value == 0:
        return None, ZERO_BASE

    # Positive -> Negative
    if start_value > 0 and end_value < 0:
        return None, DECLINE_TO_LOSS

    # Negative -> Positive
    if start_value < 0 and end_value > 0:
        return None, TURNAROUND

    # Negative -> Negative
    if start_value < 0 and end_value < 0:
        return None, BOTH_NEGATIVE

    # Positive -> Positive
    if start_value > 0 and end_value > 0:
        cagr = (
            (end_value / start_value)
            ** (1 / years)
            - 1
        ) * 100

        return cagr, NORMAL

    # Positive -> Zero
    if start_value > 0 and end_value == 0:
        return -100.0, NORMAL

    # Any remaining unsupported case
    return None, INSUFFICIENT


# =========================================================
# WINDOW HELPER
# =========================================================

def calculate_window_cagr(
    start_value: Optional[float],
    end_value: Optional[float],
    available_years: int,
    required_years: int,
) -> Tuple[Optional[float], str]:
    """
    Calculate CAGR only when the requested history exists.

    Example:
        required_years = 5
        available_years must be >= 5.
    """

    if available_years < required_years:
        return None, INSUFFICIENT

    return calculate_cagr(
        start_value,
        end_value,
        required_years,
    )










# =========================================================
# DAY 10 - DATABASE CAGR ENGINE
# =========================================================

import sqlite3
from pathlib import Path

import pandas as pd


DB_PATH = Path("nifty100.db")
CAGR_OUTPUT = Path("output/day10_cagr.csv")

CAGR_WINDOWS = (3, 5, 10)

METRICS = {
    "revenue": "sales",
    "pat": "net_profit",
    "eps": "eps",
}


def fiscal_year_number(year_label: str) -> Optional[int]:
    """
    Extract fiscal-year number from YYYY-MM.

    Example:
        '2024-03' -> 2024
        '2012-12' -> 2012
    """

    if year_label is None:
        return None

    try:
        return int(str(year_label)[:4])
    except (TypeError, ValueError):
        return None


def build_cagr_engine() -> pd.DataFrame:
    """
    Calculate Revenue, PAT and EPS CAGR for
    3Y, 5Y and 10Y windows.

    Historical endpoints are matched by actual fiscal-year
    number rather than by row position.
    """

    connection = sqlite3.connect(DB_PATH)

    query = """
    SELECT
        company_id,
        year,
        sales,
        net_profit,
        eps
    FROM profitandloss
    ORDER BY company_id, year
    """

    df = pd.read_sql_query(query, connection)
    connection.close()

    # -----------------------------------------------------
    # Normalise source values
    # -----------------------------------------------------

    df["fiscal_year"] = (
        df["year"]
        .apply(fiscal_year_number)
    )

    for column in ["sales", "net_profit", "eps"]:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )

    # -----------------------------------------------------
    # Build fast lookup:
    #
    # (company_id, fiscal_year) -> source row
    # -----------------------------------------------------

    lookup = {}

    for _, row in df.iterrows():

        if pd.isna(row["fiscal_year"]):
            continue

        key = (
            row["company_id"],
            int(row["fiscal_year"]),
        )

        lookup[key] = row

    results = []

    # -----------------------------------------------------
    # Calculate CAGR for every company-year observation
    # -----------------------------------------------------

    for _, current in df.iterrows():

        company_id = current["company_id"]
        year = current["year"]

        if pd.isna(current["fiscal_year"]):
            continue

        current_fy = int(current["fiscal_year"])

        output_row = {
            "company_id": company_id,
            "year": year,
        }

        for metric_name, source_column in METRICS.items():

            end_value = current[source_column]

            for window in CAGR_WINDOWS:

                target_fy = current_fy - window

                historical = lookup.get(
                    (company_id, target_fy)
                )

                cagr_column = (
                    f"{metric_name}_cagr_{window}yr"
                )

                flag_column = (
                    f"{metric_name}_cagr_{window}yr_flag"
                )

                # Required historical endpoint absent
                if historical is None:

                    output_row[cagr_column] = None
                    output_row[flag_column] = INSUFFICIENT

                    continue

                start_value = historical[source_column]

                # Convert pandas NaN to None so the core
                # CAGR function handles missing data safely.
                if pd.isna(start_value):
                    start_value = None

                if pd.isna(end_value):
                    safe_end_value = None
                else:
                    safe_end_value = end_value

                value, flag = calculate_cagr(
                    start_value=start_value,
                    end_value=safe_end_value,
                    years=window,
                )

                output_row[cagr_column] = value
                output_row[flag_column] = flag

        results.append(output_row)

    result = pd.DataFrame(results)

    # -----------------------------------------------------
    # Save Day 10 output
    # -----------------------------------------------------

    CAGR_OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    result.to_csv(
        CAGR_OUTPUT,
        index=False,
    )

    return result


def print_cagr_summary(result: pd.DataFrame) -> None:
    """Print Day 10 QA summary."""

    print(
        "\n=== SPRINT 2 - DAY 10 CAGR ENGINE ==="
    )

    print(
        "Rows processed:",
        len(result),
    )

    print("\nCAGR availability:")

    for metric in METRICS:

        for window in CAGR_WINDOWS:

            column = f"{metric}_cagr_{window}yr"

            print(
                f"{column:<22}:",
                result[column].notna().sum(),
            )

    print("\nFlag distributions:")

    for metric in METRICS:

        for window in CAGR_WINDOWS:

            flag_column = (
                f"{metric}_cagr_{window}yr_flag"
            )

            print(f"\n{flag_column}:")

            print(
                result[flag_column]
                .value_counts(dropna=False)
            )

    print(
        "\nSaved:",
        CAGR_OUTPUT,
    )


if __name__ == "__main__":
    cagr_result = build_cagr_engine()
    print_cagr_summary(cagr_result)