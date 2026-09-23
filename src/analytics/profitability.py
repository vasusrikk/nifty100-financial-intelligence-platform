"""Profitability ratio engine for Nifty 100."""

import sqlite3
from pathlib import Path

import pandas as pd

DB_PATH = Path("nifty100.db")
OUTPUT_PATH = Path("output/profitability_ratios.csv")


def safe_divide(numerator, denominator):
    """Return percentage ratio safely."""
    if pd.isna(numerator) or pd.isna(denominator):
        return None

    if denominator == 0:
        return None

    return (numerator / denominator) * 100


def calculate_profitability():
    """Calculate NPM, OPM, ROE and ROCE."""

    conn = sqlite3.connect(DB_PATH)

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
        b.borrowings
    FROM profitandloss p
    LEFT JOIN balancesheet b
        ON p.company_id = b.company_id
       AND p.year = b.year
    ORDER BY p.company_id, p.year
    """

    df = pd.read_sql_query(query, conn)
    conn.close()

    # Shareholders' equity
    df["equity"] = (
        pd.to_numeric(df["equity_capital"], errors="coerce")
        + pd.to_numeric(df["reserves"], errors="coerce")
    )

    # Capital employed
    df["capital_employed"] = (
        df["equity"]
        + pd.to_numeric(df["borrowings"], errors="coerce")
    )

    # Net Profit Margin
    df["npm_pct"] = df.apply(
        lambda row: safe_divide(
            row["net_profit"],
            row["sales"],
        ),
        axis=1,
    )

    # Operating Profit Margin
    df["opm_pct"] = df.apply(
        lambda row: safe_divide(
            row["operating_profit"],
            row["sales"],
        ),
        axis=1,
    )

    # Return on Equity
    df["roe_pct"] = df.apply(
        lambda row: safe_divide(
            row["net_profit"],
            row["equity"],
        ),
        axis=1,
    )

    # ROCE approximation using operating profit / capital employed
    df["roce_pct"] = df.apply(
        lambda row: safe_divide(
            row["operating_profit"],
            row["capital_employed"],
        ),
        axis=1,
    )

       # Cross-check calculated OPM against source OPM.
    df["opm_difference"] = (
        pd.to_numeric(df["source_opm"], errors="coerce")
        - df["opm_pct"]
    ).abs()

    def validate_opm(row):
        """Classify source-vs-calculated OPM."""
        if pd.isna(row["source_opm"]) or pd.isna(row["opm_pct"]):
            return "MISSING"

        if row["opm_difference"] < 1.0:
            return "PASS"

        return "MISMATCH"

    df["opm_validation"] = df.apply(
        validate_opm,
        axis=1,
    )

    output_columns = [
        "company_id",
        "year",
        "npm_pct",
        "opm_pct",
        "roe_pct",
        "roce_pct",
        "source_opm",
        "opm_difference",
        "opm_validation",
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
def main():
    result = calculate_profitability()

    print("=== D08 PROFITABILITY ENGINE ===")
    print("Rows calculated:", len(result))

    print(
        "NPM available:",
        result["npm_pct"].notna().sum(),
    )

    print(
        "OPM available:",
        result["opm_pct"].notna().sum(),
    )

    print(
        "ROE available:",
        result["roe_pct"].notna().sum(),
    )

    print(
        "ROCE available:",
        result["roce_pct"].notna().sum(),
    )

    print("\nOPM validation:")
    print(
        result["opm_validation"]
        .value_counts(dropna=False)
    )

    print(
        "\nSaved:",
        OUTPUT_PATH,
    )


if __name__ == "__main__":
    main()