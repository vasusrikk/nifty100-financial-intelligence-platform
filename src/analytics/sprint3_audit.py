"""Sprint 3 - Day 21: Final Data Quality and Completion Audit."""

from __future__ import annotations

import math
import sqlite3
from collections import defaultdict
from pathlib import Path

from src.analytics.peer import PEER_METRICS
from src.analytics.radar import RADAR_METRICS
from src.screener.scoring import SCORING_WEIGHTS


DATABASE_PATH = Path("nifty100.db")

EXPECTED_UNIVERSE = 92
EXPECTED_BROAD_SECTORS = 10
EXPECTED_PEER_GROUPS = 11
EXPECTED_PEER_MEMBERSHIPS = 56
EXPECTED_PEER_METRICS = 15
EXPECTED_PERCENTILE_ROWS = 840
EXPECTED_BENCHMARKS = 11

EXPECTED_RADAR_METRICS = 6


# ============================================================
# GENERIC HELPERS
# ============================================================

def table_exists(connection, table_name):
    """Return True if a SQLite table exists."""

    row = connection.execute(
        """
        SELECT 1
        FROM sqlite_master
        WHERE type = 'table'
          AND name = ?
        """,
        (table_name,),
    ).fetchone()

    return row is not None


def get_columns(connection, table_name):
    """Return column names for a SQLite table."""

    rows = connection.execute(
        f"PRAGMA table_info({table_name})"
    ).fetchall()

    return [
        row[1]
        for row in rows
    ]


def finite_number(value):
    """Return True only for finite numeric values."""

    if value is None:
        return False

    try:
        number = float(value)
    except (TypeError, ValueError):
        return False

    return math.isfinite(number)


# ============================================================
# CORE DATABASE AUDIT
# ============================================================

def audit_core_database(connection):
    """
    Validate core Sprint 3 database structure.
    """

    checks = []

    companies_exists = table_exists(
        connection,
        "companies",
    )

    checks.append({
        "name": "companies table exists",
        "passed": companies_exists,
        "actual": companies_exists,
        "expected": True,
    })

    sectors_exists = table_exists(
        connection,
        "sectors",
    )

    checks.append({
        "name": "sectors table exists",
        "passed": sectors_exists,
        "actual": sectors_exists,
        "expected": True,
    })

    peer_exists = table_exists(
        connection,
        "peer_percentiles",
    )

    checks.append({
        "name": "peer_percentiles table exists",
        "passed": peer_exists,
        "actual": peer_exists,
        "expected": True,
    })

    if companies_exists:

        company_count = connection.execute(
            """
            SELECT COUNT(*)
            FROM companies
            """
        ).fetchone()[0]

        checks.append({
            "name": "company universe",
            "passed":
                company_count
                == EXPECTED_UNIVERSE,
            "actual": company_count,
            "expected": EXPECTED_UNIVERSE,
        })

        duplicate_ids = connection.execute(
            """
            SELECT COUNT(*)
            FROM (
                SELECT id
                FROM companies
                GROUP BY id
                HAVING COUNT(*) > 1
            )
            """
        ).fetchone()[0]

        checks.append({
            "name": "duplicate company IDs",
            "passed": duplicate_ids == 0,
            "actual": duplicate_ids,
            "expected": 0,
        })

    if sectors_exists:

        sector_columns = get_columns(
            connection,
            "sectors",
        )

        if "broad_sector" in sector_columns:

            broad_sector_count = (
                connection.execute(
                    """
                    SELECT COUNT(
                        DISTINCT broad_sector
                    )
                    FROM sectors
                    WHERE broad_sector IS NOT NULL
                    """
                ).fetchone()[0]
            )

            checks.append({
                "name": "broad sectors",
                "passed":
                    broad_sector_count
                    == EXPECTED_BROAD_SECTORS,
                "actual": broad_sector_count,
                "expected":
                    EXPECTED_BROAD_SECTORS,
            })

    return checks


# ============================================================
# SCORING CONFIGURATION AUDIT
# ============================================================

def audit_scoring():
    """
    Validate Day 17 scoring configuration.
    """

    checks = []

    metric_count = len(
        SCORING_WEIGHTS
    )

    checks.append({
        "name": "scoring metric count",
        "passed": metric_count == 8,
        "actual": metric_count,
        "expected": 8,
    })

    weight_total = sum(
        SCORING_WEIGHTS.values()
    )

    checks.append({
        "name": "scoring weight total",
        "passed":
            math.isclose(
                weight_total,
                1.0,
                rel_tol=1e-9,
                abs_tol=1e-9,
            ),
        "actual": round(
            weight_total,
            6,
        ),
        "expected": 1.0,
    })

    invalid_weights = [
        metric
        for metric, weight
        in SCORING_WEIGHTS.items()
        if (
            not finite_number(weight)
            or weight <= 0
        )
    ]

    checks.append({
        "name": "positive scoring weights",
        "passed":
            len(invalid_weights) == 0,
        "actual":
            len(invalid_weights),
        "expected": 0,
    })

    return checks


# ============================================================
# PEER PERCENTILE AUDIT
# ============================================================

def audit_peer_percentiles(connection):
    """
    Validate persisted Day 18 peer analytics.
    """

    checks = []

    if not table_exists(
        connection,
        "peer_percentiles",
    ):
        return [{
            "name":
                "peer percentile audit available",
            "passed": False,
            "actual": "missing table",
            "expected":
                "peer_percentiles table",
        }]

    rows = connection.execute(
        """
        SELECT
            peer_group_name,
            company_id,
            is_benchmark,
            metric,
            raw_value,
            percentile
        FROM peer_percentiles
        """
    ).fetchall()

    row_count = len(rows)

    checks.append({
        "name": "peer percentile rows",
        "passed":
            row_count
            == EXPECTED_PERCENTILE_ROWS,
        "actual": row_count,
        "expected":
            EXPECTED_PERCENTILE_ROWS,
    })

    groups = {
        row[0]
        for row in rows
    }

    checks.append({
        "name": "peer groups",
        "passed":
            len(groups)
            == EXPECTED_PEER_GROUPS,
        "actual": len(groups),
        "expected":
            EXPECTED_PEER_GROUPS,
    })

    memberships = {
        (
            row[0],
            row[1],
        )
        for row in rows
    }

    checks.append({
        "name": "peer memberships",
        "passed":
            len(memberships)
            == EXPECTED_PEER_MEMBERSHIPS,
        "actual": len(memberships),
        "expected":
            EXPECTED_PEER_MEMBERSHIPS,
    })

    metrics = {
        row[3]
        for row in rows
    }

    checks.append({
        "name": "peer metric count",
        "passed":
            len(metrics)
            == EXPECTED_PEER_METRICS,
        "actual": len(metrics),
        "expected":
            EXPECTED_PEER_METRICS,
    })

    checks.append({
        "name": "peer metric configuration",
        "passed":
            metrics
            == set(PEER_METRICS),
        "actual": len(metrics),
        "expected":
            len(PEER_METRICS),
    })

    # --------------------------------------------------------
    # Exactly 15 metric rows per membership
    # --------------------------------------------------------

    membership_metrics = defaultdict(
        set
    )

    for row in rows:

        membership_metrics[
            (
                row[0],
                row[1],
            )
        ].add(
            row[3]
        )

    invalid_memberships = [
        key
        for key, metric_set
        in membership_metrics.items()
        if len(metric_set)
        != EXPECTED_PEER_METRICS
    ]

    checks.append({
        "name":
            "15 metrics per peer membership",
        "passed":
            len(invalid_memberships) == 0,
        "actual":
            len(invalid_memberships),
        "expected": 0,
    })

    # --------------------------------------------------------
    # Benchmark integrity
    # --------------------------------------------------------

    benchmark_companies = defaultdict(
        set
    )

    for (
        group_name,
        company_id,
        is_benchmark,
        _,
        _,
        _,
    ) in rows:

        if is_benchmark:
            benchmark_companies[
                group_name
            ].add(company_id)

    benchmark_count = sum(
        len(values)
        for values
        in benchmark_companies.values()
    )

    checks.append({
        "name": "benchmark companies",
        "passed":
            benchmark_count
            == EXPECTED_BENCHMARKS,
        "actual": benchmark_count,
        "expected":
            EXPECTED_BENCHMARKS,
    })

    bad_benchmark_groups = [
        group
        for group in groups
        if len(
            benchmark_companies[group]
        ) != 1
    ]

    checks.append({
        "name":
            "one benchmark per peer group",
        "passed":
            len(bad_benchmark_groups) == 0,
        "actual":
            len(bad_benchmark_groups),
        "expected": 0,
    })

    # --------------------------------------------------------
    # Percentile integrity
    # --------------------------------------------------------

    populated = [
        row[5]
        for row in rows
        if row[5] is not None
    ]

    missing = (
        row_count
        - len(populated)
    )

    invalid_percentiles = [
        value
        for value in populated
        if (
            not finite_number(value)
            or value < 0
            or value > 100
        )
    ]

    checks.append({
        "name":
            "percentiles within 0-100",
        "passed":
            len(invalid_percentiles) == 0,
        "actual":
            len(invalid_percentiles),
        "expected": 0,
    })

    checks.append({
        "name":
            "populated peer percentiles",
        "passed":
            len(populated) == 818,
        "actual": len(populated),
        "expected": 818,
    })

    checks.append({
        "name":
            "missing peer percentiles",
        "passed":
            missing == 22,
        "actual": missing,
        "expected": 22,
    })

    missing_source_mismatch = 0

    for row in rows:

        raw_value = row[4]
        percentile = row[5]

        if (
            raw_value is None
            and percentile is not None
        ):
            missing_source_mismatch += 1

    checks.append({
        "name":
            "missing source values not fabricated",
        "passed":
            missing_source_mismatch == 0,
        "actual":
            missing_source_mismatch,
        "expected": 0,
    })

    return checks


# ============================================================
# RADAR CONFIGURATION AUDIT
# ============================================================

def audit_radar():
    """
    Validate Day 19 radar configuration.
    """

    checks = []

    metric_count = len(
        RADAR_METRICS
    )

    checks.append({
        "name": "radar metric count",
        "passed":
            metric_count
            == EXPECTED_RADAR_METRICS,
        "actual": metric_count,
        "expected":
            EXPECTED_RADAR_METRICS,
    })

    metric_names = [
        metric
        for metric, _
        in RADAR_METRICS
    ]

    checks.append({
        "name": "unique radar metrics",
        "passed":
            len(metric_names)
            == len(set(metric_names)),
        "actual":
            len(set(metric_names)),
        "expected":
            EXPECTED_RADAR_METRICS,
    })

    return checks


# ============================================================
# SOURCE-LIMITATION AUDIT
# ============================================================

def audit_source_limitations(connection):
    """
    Report known source-data limitations.

    These are informational and do not cause Sprint failure
    when they are preserved rather than fabricated.
    """

    limitations = []

    if table_exists(
        connection,
        "peer_percentiles",
    ):

        missing = connection.execute(
            """
            SELECT COUNT(*)
            FROM peer_percentiles
            WHERE percentile IS NULL
            """
        ).fetchone()[0]

        if missing:
            limitations.append(
                f"{missing} peer percentile rows "
                "remain NULL because source metric "
                "values are unavailable."
            )

    limitations.append(
        "Peer percentile analytics cover the 56 "
        "companies explicitly assigned to the "
        "supplied 11 peer groups; the remaining "
        "companies in the 92-company universe are "
        "not assigned fabricated peer groups."
    )

    limitations.append(
        "Preset conditions requiring explicit free "
        "cash flow cannot be fully evaluated when "
        "the required Capex source field is absent."
    )

    return limitations


# ============================================================
# COMPLETE AUDIT
# ============================================================

def run_sprint3_audit(
    database_path=DATABASE_PATH,
):
    """
    Execute complete Sprint 3 final audit.
    """

    connection = sqlite3.connect(
        database_path
    )

    try:

        checks = []

        checks.extend(
            audit_core_database(
                connection
            )
        )

        checks.extend(
            audit_scoring()
        )

        checks.extend(
            audit_peer_percentiles(
                connection
            )
        )

        checks.extend(
            audit_radar()
        )

        limitations = (
            audit_source_limitations(
                connection
            )
        )

    finally:
        connection.close()

    passed = sum(
        check["passed"]
        for check in checks
    )

    failed = len(checks) - passed

    return {
        "checks": checks,
        "total_checks": len(checks),
        "passed": passed,
        "failed": failed,
        "limitations": limitations,
        "status":
            "PASS"
            if failed == 0
            else "FAIL",
    }


# ============================================================
# DAY 21 QA OUTPUT
# ============================================================

def main():

    result = run_sprint3_audit()

    print(
        "\n=== ORIGINAL SPRINT 3 - "
        "DAY 21 FINAL DATA QUALITY AUDIT ==="
    )

    print(
        "Status:",
        result["status"],
    )

    print(
        "Checks:",
        result["total_checks"],
    )

    print(
        "Passed:",
        result["passed"],
    )

    print(
        "Failed:",
        result["failed"],
    )

    print(
        "\nAUDIT CHECKS"
    )

    for check in result["checks"]:

        marker = (
            "PASS"
            if check["passed"]
            else "FAIL"
        )

        print(
            marker,
            "|",
            check["name"],
            "| Actual:",
            check["actual"],
            "| Expected:",
            check["expected"],
        )

    print(
        "\nSOURCE LIMITATIONS"
    )

    for index, limitation in enumerate(
        result["limitations"],
        start=1,
    ):

        print(
            index,
            "|",
            limitation,
        )


if __name__ == "__main__":
    main()