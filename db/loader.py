"""Build and populate the Nifty 100 SQLite database."""

import sqlite3
import time
from datetime import datetime
from pathlib import Path

import pandas as pd

from src.etl.loader import load_all_sources

DB_PATH = Path("nifty100.db")
SCHEMA_PATH = Path("db/schema.sql")
AUDIT_PATH = Path("output/load_audit.csv")
REJECT_PATH = Path("output/rejected_rows.csv")

ANNUAL_TABLES = {
    "profitandloss",
    "balancesheet",
    "cashflow",
}

YEAR_TABLES = {
    "profitandloss",
    "balancesheet",
    "cashflow",
    "documents",
    "market_cap",
}


def clean_value(value):
    """Convert pandas missing values to SQLite NULL."""
    if pd.isna(value):
        return None

    if hasattr(value, "item"):
        try:
            return value.item()
        except (ValueError, AttributeError):
            pass

    return value


def prepare_table(name, df, valid_ids):
    """Apply critical DQ handling before insertion."""

    df = df.copy()
    rejected = []

    # DQ-03: reject orphan company IDs
    if "company_id" in df.columns:
        orphan_mask = ~df["company_id"].isin(valid_ids)

        if orphan_mask.any():
            bad = df[orphan_mask].copy()
            bad["reject_rule"] = "DQ-03"
            bad["reject_reason"] = (
                "company_id not found in companies"
            )
            bad["source_table"] = name
            rejected.append(bad)

            df = df[~orphan_mask].copy()

    # DQ-07: reject invalid financial years
    if name in YEAR_TABLES:
        year_col = "Year" if name == "documents" else "year"

        if year_col in df.columns:
            invalid = df[year_col].astype(str).eq("PARSE_ERROR")

            if invalid.any():
                bad = df[invalid].copy()
                bad["reject_rule"] = "DQ-07"
                bad["reject_reason"] = (
                    "Unparseable financial year"
                )
                bad["source_table"] = name
                rejected.append(bad)

                df = df[~invalid].copy()

    # DQ-02: remove duplicate annual records
    if name in ANNUAL_TABLES:
        duplicate_mask = df.duplicated(
            subset=["company_id", "year"],
            keep="last",
        )

        if duplicate_mask.any():
            bad = df[duplicate_mask].copy()
            bad["reject_rule"] = "DQ-02"
            bad["reject_reason"] = (
                "Duplicate (company_id, year); "
                "last occurrence retained"
            )
            bad["source_table"] = name
            rejected.append(bad)

            df = df[~duplicate_mask].copy()

    if rejected:
        rejected_df = pd.concat(
            rejected,
            ignore_index=True,
            sort=False,
        )
    else:
        rejected_df = pd.DataFrame()

    return df, rejected_df


def insert_dataframe(conn, table, df):
    """Insert DataFrame records into SQLite."""

    if df.empty:
        return 0

    columns = list(df.columns)

    placeholders = ", ".join(
        ["?"] * len(columns)
    )

    column_sql = ", ".join(
        f'"{column}"' for column in columns
    )

    sql = (
        f'INSERT INTO "{table}" '
        f'({column_sql}) '
        f'VALUES ({placeholders})'
    )

    rows = [
        tuple(clean_value(value) for value in row)
        for row in df.itertuples(
            index=False,
            name=None,
        )
    ]

    conn.executemany(sql, rows)

    return len(rows)


def build_database():
    """Create database, load tables and generate audit."""

    datasets = load_all_sources()

    companies = datasets["companies"].copy()

    companies["id"] = (
        companies["id"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    datasets["companies"] = companies

    valid_ids = set(companies["id"])

    audit = []
    all_rejected = []

    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)

    try:
        conn.execute("PRAGMA foreign_keys = ON")

        schema = SCHEMA_PATH.read_text(
            encoding="utf-8"
        )

        conn.executescript(schema)

        # Module 1 database output = 10 tables.
        load_order = [
            "companies",
            "profitandloss",
            "balancesheet",
            "cashflow",
            "analysis",
            "documents",
            "prosandcons",
            "sectors",
            "market_cap",
            "stock_prices",
        ]

        for table in load_order:

            started = time.perf_counter()

            source = datasets[table]
            rows_in = len(source)

            if table == "companies":
                cleaned = source.copy()
                rejected = pd.DataFrame()
            else:
                cleaned, rejected = prepare_table(
                    table,
                    source,
                    valid_ids,
                )

            if not rejected.empty:
                all_rejected.append(rejected)

            rows_out = insert_dataframe(
                conn,
                table,
                cleaned,
            )

            runtime_s = (
                time.perf_counter() - started
            )

            rejected_count = (
                rows_in - rows_out
            )

            audit.append({
                "table": table,
                "rows_in": rows_in,
                "rows_out": rows_out,
                "rejected": rejected_count,
                "timestamp": datetime.now().isoformat(
                    timespec="seconds"
                ),
                "runtime_s": round(runtime_s, 4),
            })

            print(
                f"{table:<20} "
                f"in={rows_in:<5} "
                f"out={rows_out:<5} "
                f"rejected={rejected_count:<5} "
                f"runtime={runtime_s:.4f}s"
            )

        conn.commit()

        fk_errors = conn.execute(
            "PRAGMA foreign_key_check"
        ).fetchall()

        if fk_errors:
            raise RuntimeError(
                f"Foreign-key failures: {fk_errors}"
            )

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()

    AUDIT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    pd.DataFrame(
        audit,
        columns=[
            "table",
            "rows_in",
            "rows_out",
            "rejected",
            "timestamp",
            "runtime_s",
        ],
    ).to_csv(
        AUDIT_PATH,
        index=False,
    )

    if all_rejected:
        pd.concat(
            all_rejected,
            ignore_index=True,
            sort=False,
        ).to_csv(
            REJECT_PATH,
            index=False,
        )

    print("\nDatabase created:", DB_PATH)
    print("Audit created:", AUDIT_PATH)
    print("Rejected rows:", REJECT_PATH)
    print("Foreign-key integrity: PASSED")


if __name__ == "__main__":
    build_database()