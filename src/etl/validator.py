"""Data-quality validator for the Nifty 100 ETL pipeline."""

import re
from pathlib import Path

import pandas as pd

from src.etl.loader import load_all_sources

OUTPUT = Path("output/validation_failures.csv")

YEAR_PATTERN = re.compile(r"^\d{4}-\d{2}$")
TICKER_PATTERN = re.compile(r"^.{2,12}$")


def failure(
    rows,
    rule,
    severity,
    table,
    company_id,
    message,
    year="",
    field="",
):
    """Record one data-quality violation."""
    rows.append({
        "rule": rule,
        "table": table,
        "company_id": company_id,
        "year": year,
        "field": field,
        "issue": message,
        "severity": severity,
    })


def validate():
    data = load_all_sources()
    failures = []

    companies = data["companies"]
    pl = data["profitandloss"]
    bs = data["balancesheet"]
    cf = data["cashflow"]

    valid_ids = set(
        companies["id"].dropna().astype(str).str.strip().str.upper()
    )

    # DQ-01: Company PK uniqueness
    dup = companies[companies["id"].duplicated(keep=False)]
    for _, row in dup.iterrows():
        failure(
            failures, "DQ-01", "CRITICAL", "companies",
            row["id"], "Duplicate company primary key"
        )

    # DQ-02: Annual PK uniqueness
    for table_name in ["profitandloss", "balancesheet", "cashflow"]:
        df = data[table_name]

        duplicates = df[
            df.duplicated(["company_id", "year"], keep=False)
        ]

        for _, row in duplicates.iterrows():
            failure(
                failures, "DQ-02", "CRITICAL", table_name,
                row["company_id"],
                f"Duplicate annual record: {row['year']}"
            )

    # DQ-03: Foreign-key integrity
    for table_name, df in data.items():
        if "company_id" not in df.columns:
            continue

        for _, row in df.iterrows():
            cid = str(row["company_id"]).strip().upper()

            if cid not in valid_ids:
                failure(
                    failures, "DQ-03", "CRITICAL",
                    table_name, cid,
                    "company_id not found in companies"
                )

    # DQ-04: Balance-sheet balance
    for _, row in bs.iterrows():
        assets = pd.to_numeric(row["total_assets"], errors="coerce")
        liabilities = pd.to_numeric(
            row["total_liabilities"], errors="coerce"
        )

        if pd.notna(assets) and pd.notna(liabilities) and assets != 0:
            difference = abs(assets - liabilities) / abs(assets)

            if difference >= 0.01:
                failure(
                    failures, "DQ-04", "WARNING",
                    "balancesheet", row["company_id"],
                    "Assets/liabilities difference >= 1%"
                )

    # DQ-05: OPM cross-check
    for _, row in pl.iterrows():
        sales = pd.to_numeric(row["sales"], errors="coerce")
        op = pd.to_numeric(
            row["operating_profit"], errors="coerce"
        )
        source_opm = pd.to_numeric(
            row["opm_percentage"], errors="coerce"
        )

        if (
            pd.notna(sales)
            and sales != 0
            and pd.notna(op)
            and pd.notna(source_opm)
        ):
            computed = op / sales * 100

            if abs(source_opm - computed) >= 1.0:
                failure(
                    failures, "DQ-05", "WARNING",
                    "profitandloss", row["company_id"],
                    f"Source OPM={source_opm}; computed={computed:.2f}"
                )

    # DQ-06: Positive sales
    sales_values = pd.to_numeric(pl["sales"], errors="coerce")

    for _, row in pl[sales_values <= 0].iterrows():
        failure(
            failures, "DQ-06", "WARNING",
            "profitandloss", row["company_id"],
            "Sales <= 0"
        )

    # DQ-07: Year format
    for table_name, df in data.items():
        year_col = None

        if "year" in df.columns:
            year_col = "year"
        elif "Year" in df.columns:
            year_col = "Year"

        if year_col is None:
            continue

        for _, row in df.iterrows():
            year = str(row[year_col])

            if not YEAR_PATTERN.fullmatch(year):
                failure(
                    failures, "DQ-07", "CRITICAL",
                    table_name,
                    row.get("company_id", ""),
                    f"Invalid year: {year}"
                )

    # DQ-08: Ticker format
    for table_name, df in data.items():
        if "company_id" not in df.columns:
            continue

        for _, row in df.iterrows():
            cid = str(row["company_id"]).strip().upper()

            if not TICKER_PATTERN.fullmatch(cid):
                failure(
                    failures, "DQ-08", "CRITICAL",
                    table_name, cid,
                    "Ticker length outside 2-12 characters"
                )

    # DQ-09: Net cash-flow reconciliation
    for _, row in cf.iterrows():
        cfo = pd.to_numeric(
            row["operating_activity"], errors="coerce"
        )
        cfi = pd.to_numeric(
            row["investing_activity"], errors="coerce"
        )
        cff = pd.to_numeric(
            row["financing_activity"], errors="coerce"
        )
        net = pd.to_numeric(
            row["net_cash_flow"], errors="coerce"
        )

        if all(pd.notna(x) for x in [cfo, cfi, cff, net]):
            calculated = cfo + cfi + cff

            if abs(net - calculated) > 10:
                failure(
                    failures, "DQ-09", "WARNING",
                    "cashflow", row["company_id"],
                    f"Net CF={net}; components={calculated}"
                )

    # DQ-10: Non-negative fixed assets
    fixed_assets = pd.to_numeric(
        bs["fixed_assets"], errors="coerce"
    )

    for _, row in bs[fixed_assets < 0].iterrows():
        failure(
            failures, "DQ-10", "WARNING",
            "balancesheet", row["company_id"],
            "Negative fixed assets"
        )

    # DQ-11: Tax-rate range
    tax = pd.to_numeric(
        pl["tax_percentage"], errors="coerce"
    )

    invalid_tax = pl[(tax < 0) | (tax > 60)]

    for _, row in invalid_tax.iterrows():
        failure(
            failures, "DQ-11", "WARNING",
            "profitandloss", row["company_id"],
            f"Tax percentage outside 0-60: {row['tax_percentage']}"
        )

    # DQ-12: Dividend payout cap
    dividend = pd.to_numeric(
        pl["dividend_payout"], errors="coerce"
    )

    for _, row in pl[dividend > 200].iterrows():
        failure(
            failures, "DQ-12", "WARNING",
            "profitandloss", row["company_id"],
            f"Dividend payout > 200: {row['dividend_payout']}"
        )

    # DQ-13: Annual-report URL validity.
    # Network HEAD requests are intentionally deferred so validation
    # remains deterministic/offline. Missing URLs are still logged.
    documents = data["documents"]

    for _, row in documents.iterrows():
        url = row.get("Annual_Report")

        if pd.isna(url) or not str(url).strip().lower().startswith(
            ("http://", "https://")
        ):
            failure(
                failures, "DQ-13", "WARNING",
                "documents", row["company_id"],
                "Missing or invalid Annual_Report URL"
            )

    # DQ-14: EPS sign consistency
    for _, row in pl.iterrows():
        profit = pd.to_numeric(
            row["net_profit"], errors="coerce"
        )
        eps = pd.to_numeric(row["eps"], errors="coerce")

        if (
            pd.notna(profit)
            and pd.notna(eps)
            and profit > 0
            and eps <= 0
        ):
            failure(
                failures, "DQ-14", "WARNING",
                "profitandloss", row["company_id"],
                f"Positive net profit but EPS={eps}"
            )

    # DQ-15: Strict BS balance informational counter
    for _, row in bs.iterrows():
        assets = pd.to_numeric(
            row["total_assets"], errors="coerce"
        )
        liabilities = pd.to_numeric(
            row["total_liabilities"], errors="coerce"
        )

        if (
            pd.notna(assets)
            and pd.notna(liabilities)
            and assets != liabilities
        ):
            failure(
                failures, "DQ-15", "INFO",
                "balancesheet", row["company_id"],
                "Total assets != total liabilities"
            )

    # DQ-16: Minimum five-year coverage
    for cid in valid_ids:
        for table_name in [
            "profitandloss",
            "balancesheet",
            "cashflow",
        ]:
            df = data[table_name]

            count = df[
                (df["company_id"] == cid)
                & (df["year"] != "PARSE_ERROR")
            ]["year"].nunique()

            if count < 5:
                failure(
                    failures, "DQ-16", "WARNING",
                    table_name, cid,
                    f"Only {count} years of history"
                )

    result = pd.DataFrame(
    failures,
    columns=[
        "rule",
        "table",
        "company_id",
        "year",
        "field",
        "issue",
        "severity",
    ],
)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(OUTPUT, index=False)

    return result


def main():
    result = validate()

    print(f"\nTotal validation failures: {len(result)}")

    if not result.empty:
        print("\nBy severity:")
        print(result["severity"].value_counts())

        print("\nBy rule:")
        print(result.groupby(["rule", "severity"]).size())

    print(f"\nSaved: {OUTPUT}")


if __name__ == "__main__":
    main() 