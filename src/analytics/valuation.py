"""Sprint 4 - Day 26: Valuation Summary Engine.

Creates a 2024-03 valuation summary for the complete 92-company
universe using P/E, P/B and EV/EBITDA.

Valuation flags are sector-relative. FCF yield is intentionally
left unavailable when source FCF is missing.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd


DATABASE_PATH = Path("nifty100.db")
OUTPUT_PATH = Path("reports") / "valuation_summary.xlsx"
VALUATION_YEAR = "2024-03"

VALUATION_METRICS = [
    "pe_ratio",
    "pb_ratio",
    "ev_ebitda",
]


def load_valuation_data(
    db_path=DATABASE_PATH,
    year=VALUATION_YEAR,
):
    """Load valuation data and sector classifications."""

    query = """
        SELECT
            c.id AS company_id,
            c.company_name,
            s.broad_sector,
            s.sub_sector,
            s.market_cap_category,
            mc.year,
            mc.market_cap_crore,
            mc.enterprise_value_crore,
            mc.pe_ratio,
            mc.pb_ratio,
            mc.ev_ebitda,
            mc.dividend_yield_pct,
            fr.fcf
        FROM companies c
        LEFT JOIN sectors s
            ON s.company_id = c.id
        LEFT JOIN market_cap mc
            ON mc.company_id = c.id
            AND mc.year = ?
        LEFT JOIN financial_ratios fr
            ON fr.company_id = c.id
            AND fr.year = ?
        ORDER BY c.company_name
    """

    with sqlite3.connect(db_path) as connection:
        return pd.read_sql_query(
            query,
            connection,
            params=(year, year),
        )


def add_sector_benchmarks(rows):
    """Add sector median valuation multiples."""

    result = rows.copy()

    for metric in VALUATION_METRICS:
        result[
            f"sector_median_{metric}"
        ] = (
            result.groupby("broad_sector")[
                metric
            ]
            .transform("median")
        )

    return result


def classify_metric(value, sector_median):
    """
    Classify valuation relative to the sector median.

    Project specification:
    - Above 1.5x sector median -> Caution
    - Below 0.7x sector median -> Discount
    - Otherwise -> In Line
    """

    if (
        pd.isna(value)
        or pd.isna(sector_median)
        or sector_median <= 0
    ):
        return "Unavailable"

    if value > sector_median * 1.5:
        return "Caution"

    if value < sector_median * 0.7:
        return "Discount"

    return "In Line"
def add_valuation_flags(rows):
    """Create transparent sector-relative valuation flags."""

    result = rows.copy()

    for metric in VALUATION_METRICS:
        result[
            f"{metric}_flag"
        ] = result.apply(
            lambda row: classify_metric(
                row[metric],
                row[
                    f"sector_median_{metric}"
                ],
            ),
            axis=1,
        )

    return result


def add_fcf_yield(rows):
    """
    Calculate FCF yield only when genuine FCF and market-cap
    source values are available.

    No FCF value is derived from incomplete Capex data.
    """

    result = rows.copy()

    def calculate(row):
        fcf = row["fcf"]
        market_cap = row["market_cap_crore"]

        if (
            pd.isna(fcf)
            or pd.isna(market_cap)
            or market_cap <= 0
        ):
            return None

        return (
            float(fcf)
            / float(market_cap)
        ) * 100

    result["fcf_yield_pct"] = result.apply(
        calculate,
        axis=1,
    )

    result["fcf_yield_status"] = (
        result["fcf_yield_pct"]
        .apply(
            lambda value:
            "Available"
            if pd.notna(value)
            else "Unavailable - source FCF absent"
        )
    )

    return result


def build_valuation_summary(
    db_path=DATABASE_PATH,
    year=VALUATION_YEAR,
):
    """Build the complete company valuation summary."""

    rows = load_valuation_data(
        db_path=db_path,
        year=year,
    )

    rows = add_sector_benchmarks(rows)
    rows = add_valuation_flags(rows)
    rows = add_fcf_yield(rows)

    return rows


def export_valuation_summary(
    output_path=OUTPUT_PATH,
    db_path=DATABASE_PATH,
    year=VALUATION_YEAR,
):
    """Export valuation summary to Excel."""

    output_path = Path(output_path)
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    summary = build_valuation_summary(
        db_path=db_path,
        year=year,
    )

    export_columns = [
        "company_id",
        "company_name",
        "broad_sector",
        "sub_sector",
        "market_cap_category",
        "year",
        "market_cap_crore",
        "enterprise_value_crore",
        "pe_ratio",
        "sector_median_pe_ratio",
        "pe_ratio_flag",
        "pb_ratio",
        "sector_median_pb_ratio",
        "pb_ratio_flag",
        "ev_ebitda",
        "sector_median_ev_ebitda",
        "ev_ebitda_flag",
        "dividend_yield_pct",
        "fcf",
        "fcf_yield_pct",
        "fcf_yield_status",
    ]

    summary[
        export_columns
    ].to_excel(
        output_path,
        index=False,
        sheet_name="Valuation Summary",
    )

    return summary


def main():
    summary = export_valuation_summary()

    print(
        "VALUATION SUMMARY ROWS:",
        len(summary),
    )

    print(
        "COMPANIES:",
        summary["company_id"].nunique(),
    )

    print(
        "PE POPULATED:",
        summary["pe_ratio"].notna().sum(),
    )

    print(
        "PB POPULATED:",
        summary["pb_ratio"].notna().sum(),
    )

    print(
        "EV/EBITDA POPULATED:",
        summary["ev_ebitda"].notna().sum(),
    )

    print(
        "FCF YIELD POPULATED:",
        summary["fcf_yield_pct"].notna().sum(),
    )

    print(
        "OUTPUT:",
        OUTPUT_PATH,
    )


if __name__ == "__main__":
    main()