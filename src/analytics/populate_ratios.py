"""Sprint 2 - Day 12 Financial Ratios Table Population."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd


# =========================================================
# PATHS
# =========================================================

DB_PATH = Path("nifty100.db")

DAY08 = Path("output/day08_profitability_ratios.csv")
DAY09 = Path("output/day09_leverage_efficiency.csv")
DAY10 = Path("output/day10_cagr.csv")
DAY11 = Path("output/day11_cashflow_kpis.csv")

MIN_REQUIRED_ROWS = 1100


# =========================================================
# COMPANY-YEAR BASE
# =========================================================

def load_company_year_base() -> pd.DataFrame:
    """
    Build the legitimate Sprint 2 company-year universe.

    The base is the UNION of company-year combinations available
    across Profit & Loss, Balance Sheet and Cash Flow.

    This prevents Day 12 from being artificially restricted to
    Profit & Loss rows only.
    """

    connection = sqlite3.connect(DB_PATH)

    query = """
        SELECT company_id, year
        FROM profitandloss

        UNION

        SELECT company_id, year
        FROM balancesheet

        UNION

        SELECT company_id, year
        FROM cashflow

        ORDER BY company_id, year
    """

    base = pd.read_sql_query(
        query,
        connection,
    )

    connection.close()

    base["company_id"] = (
        base["company_id"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    base["year"] = (
        base["year"]
        .astype(str)
        .str.strip()
    )

    base = base.drop_duplicates(
        subset=["company_id", "year"]
    ).reset_index(drop=True)

    return base


# =========================================================
# LOAD SPRINT 2 OUTPUTS
# =========================================================

def load_outputs() -> pd.DataFrame:
    """
    Load and merge Sprint 2 KPI outputs onto the complete
    company-year universe.
    """

    base = load_company_year_base()

    d8 = pd.read_csv(DAY08)
    d9 = pd.read_csv(DAY09)
    d10 = pd.read_csv(DAY10)
    d11 = pd.read_csv(DAY11)

    datasets = [d8, d9, d10, d11]

    # Standardise merge keys.
    for df in datasets:
        df["company_id"] = (
            df["company_id"]
            .astype(str)
            .str.strip()
            .str.upper()
        )

        df["year"] = (
            df["year"]
            .astype(str)
            .str.strip()
        )

    result = base.copy()

    # -----------------------------------------------------
    # DAY 08 - PROFITABILITY
    # -----------------------------------------------------

    result = result.merge(
        d8[
            [
                "company_id",
                "year",
                "npm_pct",
                "opm_pct",
                "roe_pct",
                "roce_pct",
                "roa_pct",
            ]
        ],
        on=["company_id", "year"],
        how="left",
        validate="one_to_one",
    )

    # -----------------------------------------------------
    # DAY 09 - LEVERAGE / EFFICIENCY
    # -----------------------------------------------------

    result = result.merge(
        d9[
            [
                "company_id",
                "year",
                "de_ratio",
                "leverage_flag",
                "icr",
                "icr_flag",
                "net_debt",
                "net_debt_status",
                "asset_turnover",
            ]
        ],
        on=["company_id", "year"],
        how="left",
        validate="one_to_one",
    )

    # -----------------------------------------------------
    # DAY 10 - CAGR
    # -----------------------------------------------------
    # Day 12 requires the 5-year CAGR metrics.
    # -----------------------------------------------------

    result = result.merge(
        d10[
            [
                "company_id",
                "year",
                "revenue_cagr_5yr",
                "revenue_cagr_5yr_flag",
                "pat_cagr_5yr",
                "pat_cagr_5yr_flag",
                "eps_cagr_5yr",
                "eps_cagr_5yr_flag",
            ]
        ],
        on=["company_id", "year"],
        how="left",
        validate="one_to_one",
    )

    # -----------------------------------------------------
    # DAY 11 - CASH FLOW KPIs
    # -----------------------------------------------------

    result = result.merge(
        d11[
            [
                "company_id",
                "year",
                "cfo_margin_pct",
                "cfo_pat_ratio",
                "cfo_pat_flag",
                "fcf",
                "fcf_margin_pct",
                "capex_sales_pct",
                "capex_kpi_status",
            ]
        ],
        on=["company_id", "year"],
        how="left",
        validate="one_to_one",
    )

    return result


# =========================================================
# DATABASE TABLE
# =========================================================

def create_table(
    connection: sqlite3.Connection,
) -> None:
    """Create the consolidated financial_ratios table."""

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS financial_ratios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            company_id TEXT NOT NULL,
            year TEXT NOT NULL,

            npm_pct REAL,
            opm_pct REAL,
            roe_pct REAL,
            roce_pct REAL,
            roa_pct REAL,

            de_ratio REAL,
            leverage_flag TEXT,

            icr REAL,
            icr_flag TEXT,

            net_debt REAL,
            net_debt_status TEXT,

            asset_turnover REAL,

            revenue_cagr_5yr REAL,
            revenue_cagr_5yr_flag TEXT,

            pat_cagr_5yr REAL,
            pat_cagr_5yr_flag TEXT,

            eps_cagr_5yr REAL,
            eps_cagr_5yr_flag TEXT,

            cfo_margin_pct REAL,
            cfo_pat_ratio REAL,
            cfo_pat_flag TEXT,

            fcf REAL,
            fcf_margin_pct REAL,
            capex_sales_pct REAL,
            capex_kpi_status TEXT,

            UNIQUE(company_id, year),

            FOREIGN KEY(company_id)
                REFERENCES companies(id)
        )
        """
    )


# =========================================================
# POPULATE TABLE
# =========================================================

def populate_table(
    connection: sqlite3.Connection,
    df: pd.DataFrame,
) -> None:
    """Replace financial_ratios rows transactionally."""

    columns = [
        "company_id",
        "year",
        "npm_pct",
        "opm_pct",
        "roe_pct",
        "roce_pct",
        "roa_pct",
        "de_ratio",
        "leverage_flag",
        "icr",
        "icr_flag",
        "net_debt",
        "net_debt_status",
        "asset_turnover",
        "revenue_cagr_5yr",
        "revenue_cagr_5yr_flag",
        "pat_cagr_5yr",
        "pat_cagr_5yr_flag",
        "eps_cagr_5yr",
        "eps_cagr_5yr_flag",
        "cfo_margin_pct",
        "cfo_pat_ratio",
        "cfo_pat_flag",
        "fcf",
        "fcf_margin_pct",
        "capex_sales_pct",
        "capex_kpi_status",
    ]

    clean = df[columns].copy()

    # Defensive uniqueness check.
    duplicates = clean.duplicated(
        subset=["company_id", "year"],
        keep=False,
    )

    if duplicates.any():
        raise ValueError(
            "Duplicate company-year rows detected "
            "before financial_ratios insertion."
        )

    # Convert pandas NaN / NA to SQL NULL.
    clean = clean.astype(object).where(
        pd.notna(clean),
        None,
    )

    placeholders = ",".join(
        ["?"] * len(columns)
    )

    sql = f"""
        INSERT INTO financial_ratios
        ({",".join(columns)})
        VALUES ({placeholders})
    """

    connection.execute(
        "DELETE FROM financial_ratios"
    )

    connection.executemany(
        sql,
        clean.itertuples(
            index=False,
            name=None,
        ),
    )


# =========================================================
# DAY 12 VALIDATION
# =========================================================

def validate_population(
    connection: sqlite3.Connection,
) -> None:
    """Run Sprint 2 Day 12 database QA checks."""

    row_count = connection.execute(
        """
        SELECT COUNT(*)
        FROM financial_ratios
        """
    ).fetchone()[0]

    duplicate_count = connection.execute(
        """
        SELECT COUNT(*)
        FROM (
            SELECT
                company_id,
                year
            FROM financial_ratios
            GROUP BY
                company_id,
                year
            HAVING COUNT(*) > 1
        )
        """
    ).fetchone()[0]

    fk_errors = connection.execute(
        "PRAGMA foreign_key_check"
    ).fetchall()

    print(
        "\n=== SPRINT 2 - DAY 12 "
        "FINANCIAL RATIOS POPULATION ==="
    )

    print(
        "Rows inserted:",
        row_count,
    )

    print(
        "Minimum required:",
        MIN_REQUIRED_ROWS,
    )

    print(
        "Row-count requirement:",
        (
            "PASS"
            if row_count >= MIN_REQUIRED_ROWS
            else "FAIL"
        ),
    )

    print(
        "Duplicate company-year pairs:",
        duplicate_count,
    )

    print(
        "Uniqueness:",
        (
            "PASS"
            if duplicate_count == 0
            else "FAIL"
        ),
    )

    print(
        "Foreign-key integrity:",
        (
            "PASS"
            if not fk_errors
            else "FAIL"
        ),
    )

    # -----------------------------------------------------
    # KPI AVAILABILITY
    # -----------------------------------------------------

    print(
        "\nKPI availability:"
    )

    kpi_columns = [
        "npm_pct",
        "opm_pct",
        "roe_pct",
        "roce_pct",
        "roa_pct",
        "de_ratio",
        "icr",
        "asset_turnover",
        "revenue_cagr_5yr",
        "pat_cagr_5yr",
        "eps_cagr_5yr",
        "cfo_margin_pct",
        "cfo_pat_ratio",
        "fcf",
        "fcf_margin_pct",
        "capex_sales_pct",
    ]

    for column in kpi_columns:
        count = connection.execute(
            f"""
            SELECT COUNT({column})
            FROM financial_ratios
            """
        ).fetchone()[0]

        print(
            f"{column:<22}: {count}"
        )

    # -----------------------------------------------------
    # EXPECTED SOURCE LIMITATIONS
    # -----------------------------------------------------

    print(
        "\nSource-data limitations:"
    )

    print(
        "Net Debt:",
        "explicit cash/cash-equivalent source unavailable"
    )

    print(
        "FCF / FCF Margin / Capex-Sales:",
        "explicit Capex source unavailable"
    )

    # -----------------------------------------------------
    # HARD DAY 12 ACCEPTANCE CHECKS
    # -----------------------------------------------------

    if row_count < MIN_REQUIRED_ROWS:
        raise RuntimeError(
            "Day 12 failed: financial_ratios "
            f"contains only {row_count} rows; "
            f"minimum required is {MIN_REQUIRED_ROWS}."
        )

    if duplicate_count != 0:
        raise RuntimeError(
            "Day 12 failed: duplicate "
            "company-year rows detected."
        )

    if fk_errors:
        raise RuntimeError(
            "Day 12 failed: foreign-key "
            "violations detected."
        )


# =========================================================
# MAIN
# =========================================================

def main() -> None:
    """Run Sprint 2 Day 12 population."""

    df = load_outputs()

    print(
        "Company-year base rows:",
        len(df),
    )

    connection = sqlite3.connect(
        DB_PATH
    )

    try:
        connection.execute(
            "PRAGMA foreign_keys = ON"
        )

        create_table(
            connection
        )

        populate_table(
            connection,
            df,
        )

        connection.commit()

        validate_population(
            connection
        )

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    main()