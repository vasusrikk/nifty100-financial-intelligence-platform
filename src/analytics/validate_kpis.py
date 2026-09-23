"""Sprint 2 - Day 13 KPI Edge-Case Validation."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd


DB_PATH = Path("nifty100.db")
VALIDATION_OUTPUT = Path("output/day13_kpi_validation.csv")


def run_validation() -> pd.DataFrame:
    """Run final Sprint 2 KPI validation checks."""

    connection = sqlite3.connect(DB_PATH)

    ratios = pd.read_sql_query(
        """
        SELECT *
        FROM financial_ratios
        """,
        connection,
    )

    checks = []

    # =====================================================
    # D13-01: TABLE MUST CONTAIN DATA
    # =====================================================

    checks.append(
        {
            "check_id": "D13-01",
            "check": "financial_ratios contains rows",
            "status": "PASS" if len(ratios) > 0 else "FAIL",
            "details": f"rows={len(ratios)}",
        }
    )

    # =====================================================
    # D13-02: UNIQUE COMPANY-YEAR
    # =====================================================

    duplicates = ratios.duplicated(
        subset=["company_id", "year"]
    ).sum()

    checks.append(
        {
            "check_id": "D13-02",
            "check": "No duplicate company-year rows",
            "status": "PASS" if duplicates == 0 else "FAIL",
            "details": f"duplicates={duplicates}",
        }
    )

    # =====================================================
    # D13-03: FOREIGN KEY INTEGRITY
    # =====================================================

    fk_errors = connection.execute(
        "PRAGMA foreign_key_check"
    ).fetchall()

    checks.append(
        {
            "check_id": "D13-03",
            "check": "Foreign-key integrity",
            "status": "PASS" if not fk_errors else "FAIL",
            "details": f"errors={len(fk_errors)}",
        }
    )

    # =====================================================
    # D13-04: REQUIRED PROFITABILITY METRICS
    # =====================================================

    profitability_columns = [
        "npm_pct",
        "opm_pct",
        "roe_pct",
        "roce_pct",
        "roa_pct",
    ]

    missing_profitability_columns = [
        column
        for column in profitability_columns
        if column not in ratios.columns
    ]

    checks.append(
        {
            "check_id": "D13-04",
            "check": "Profitability KPI columns present",
            "status": (
                "PASS"
                if not missing_profitability_columns
                else "FAIL"
            ),
            "details": (
                "all present"
                if not missing_profitability_columns
                else str(missing_profitability_columns)
            ),
        }
    )

    # =====================================================
    # D13-05: FINANCIAL-SECTOR CARVE-OUT
    # =====================================================

    sector_relative = (
        ratios["leverage_flag"]
        .eq("SECTOR_RELATIVE")
        .sum()
    )

    checks.append(
        {
            "check_id": "D13-05",
            "check": "Financial-sector leverage carve-out used",
            "status": "PASS" if sector_relative > 0 else "FAIL",
            "details": f"sector_relative_rows={sector_relative}",
        }
    )

    # =====================================================
    # D13-06: HIGH-LEVERAGE FLAG
    # =====================================================

    high_leverage = (
        ratios["leverage_flag"]
        .eq("HIGH_LEVERAGE")
        .sum()
    )

    checks.append(
        {
            "check_id": "D13-06",
            "check": "High-leverage classification operational",
            "status": "PASS" if high_leverage > 0 else "FAIL",
            "details": f"high_leverage_rows={high_leverage}",
        }
    )

    # =====================================================
    # D13-07: ICR EDGE CASES
    # =====================================================

    valid_icr_flags = {
        "NORMAL",
        "ICR_WARNING",
        "DEBT_FREE",
        "N/A",
    }

    observed_icr_flags = set(
        ratios["icr_flag"]
        .dropna()
        .unique()
    )

    invalid_icr_flags = (
        observed_icr_flags - valid_icr_flags
    )

    checks.append(
        {
            "check_id": "D13-07",
            "check": "ICR classifications valid",
            "status": (
                "PASS"
                if not invalid_icr_flags
                else "FAIL"
            ),
            "details": (
                f"observed={sorted(observed_icr_flags)}"
            ),
        }
    )

    # =====================================================
    # D13-08: NET DEBT SOURCE LIMITATION
    # =====================================================

    net_debt_available = (
        ratios["net_debt"]
        .notna()
        .sum()
    )

    net_debt_status_ok = (
        ratios["net_debt_status"]
        .eq("SOURCE_CASH_FIELD_UNAVAILABLE")
        .all()
    )

    checks.append(
        {
            "check_id": "D13-08",
            "check": "Net Debt source limitation documented",
            "status": (
                "PASS"
                if (
                    net_debt_available == 0
                    and net_debt_status_ok
                )
                else "FAIL"
            ),
            "details": (
                f"calculated_rows={net_debt_available}"
            ),
        }
    )

    # =====================================================
    # D13-09: CAGR FLAGS
    # =====================================================

    cagr_flag_columns = [
        "revenue_cagr_5yr_flag",
        "pat_cagr_5yr_flag",
        "eps_cagr_5yr_flag",
    ]

    valid_cagr_flags = {
        "NORMAL",
        "DECLINE_TO_LOSS",
        "TURNAROUND",
        "BOTH_NEGATIVE",
        "ZERO_BASE",
        "INSUFFICIENT",
    }

    invalid_cagr_count = 0

    for column in cagr_flag_columns:

        observed = set(
            ratios[column]
            .dropna()
            .unique()
        )

        invalid_cagr_count += len(
            observed - valid_cagr_flags
        )

    checks.append(
        {
            "check_id": "D13-09",
            "check": "CAGR edge-case flags valid",
            "status": (
                "PASS"
                if invalid_cagr_count == 0
                else "FAIL"
            ),
            "details": (
                f"invalid_flags={invalid_cagr_count}"
            ),
        }
    )

    # =====================================================
    # D13-10: CAGR INSUFFICIENT HISTORY EXISTS
    # =====================================================

    insufficient_count = sum(
        ratios[column]
        .eq("INSUFFICIENT")
        .sum()
        for column in cagr_flag_columns
    )

    checks.append(
        {
            "check_id": "D13-10",
            "check": "Insufficient CAGR history handled",
            "status": (
                "PASS"
                if insufficient_count > 0
                else "FAIL"
            ),
            "details": (
                f"insufficient_flags={insufficient_count}"
            ),
        }
    )

    # =====================================================
    # D13-11: CFO/PAT FLAGS
    # =====================================================

    valid_cfo_flags = {
        "NORMAL",
        "ZERO_PAT",
        "NEGATIVE_PAT",
        "MISSING",
    }

    observed_cfo_flags = set(
        ratios["cfo_pat_flag"]
        .dropna()
        .unique()
    )

    invalid_cfo_flags = (
        observed_cfo_flags - valid_cfo_flags
    )

    checks.append(
        {
            "check_id": "D13-11",
            "check": "CFO/PAT edge-case flags valid",
            "status": (
                "PASS"
                if not invalid_cfo_flags
                else "FAIL"
            ),
            "details": (
                f"observed={sorted(observed_cfo_flags)}"
            ),
        }
    )

    # =====================================================
    # D13-12: CAPEX SOURCE LIMITATION
    # =====================================================

    capex_metrics_available = (
        ratios[
            [
                "fcf",
                "fcf_margin_pct",
                "capex_sales_pct",
            ]
        ]
        .notna()
        .sum()
        .sum()
    )

    capex_status_rows = (
        ratios["capex_kpi_status"]
        .eq("CAPEX_SOURCE_UNAVAILABLE")
        .sum()
    )

    # Day 11 contains 1056 cash-flow rows.
    # Rows without matching Day 11 data remain NULL after
    # the left join in Day 12, which is expected.
    capex_limitation_ok = (
        capex_metrics_available == 0
        and capex_status_rows > 0
    )

    checks.append(
        {
            "check_id": "D13-12",
            "check": "Capex-dependent limitation documented",
            "status": (
                "PASS"
                if capex_limitation_ok
                else "FAIL"
            ),
            "details": (
                f"calculated_values="
                f"{capex_metrics_available}, "
                f"documented_rows="
                f"{capex_status_rows}"
            ),
        }
    )

    # =====================================================
    # D13-13: NO INFINITE NUMERIC RATIOS
    # =====================================================

    numeric_columns = [
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
    ]

    infinite_count = 0

    for column in numeric_columns:

        values = pd.to_numeric(
            ratios[column],
            errors="coerce",
        )

        infinite_count += (
            values
            .isin([float("inf"), float("-inf")])
            .sum()
        )

    checks.append(
        {
            "check_id": "D13-13",
            "check": "No infinite KPI values",
            "status": (
                "PASS"
                if infinite_count == 0
                else "FAIL"
            ),
            "details": f"infinite_values={infinite_count}",
        }
    )

    connection.close()

    result = pd.DataFrame(checks)

    VALIDATION_OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    result.to_csv(
        VALIDATION_OUTPUT,
        index=False,
    )

    return result


def print_validation_summary(
    result: pd.DataFrame,
) -> None:
    """Print final Day 13 validation report."""

    print(
        "\n=== SPRINT 2 - DAY 13 "
        "EDGE-CASE VALIDATION ==="
    )

    print("\nValidation results:")

    print(
        result[
            [
                "check_id",
                "status",
                "check",
                "details",
            ]
        ].to_string(index=False)
    )

    passed = (
        result["status"]
        .eq("PASS")
        .sum()
    )

    failed = (
        result["status"]
        .eq("FAIL")
        .sum()
    )

    print("\nSummary:")
    print("Checks passed:", passed)
    print("Checks failed:", failed)

    print(
        "\nOverall:",
        "PASS" if failed == 0 else "FAIL",
    )

    print("\nSaved:", VALIDATION_OUTPUT)


if __name__ == "__main__":
    validation = run_validation()
    print_validation_summary(validation)