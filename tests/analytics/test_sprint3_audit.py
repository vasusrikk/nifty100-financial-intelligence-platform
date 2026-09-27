"""Tests for Sprint 3 - Day 21 final data-quality audit."""

import sqlite3

from src.analytics.sprint3_audit import (
    EXPECTED_BENCHMARKS,
    EXPECTED_BROAD_SECTORS,
    EXPECTED_PEER_GROUPS,
    EXPECTED_PEER_MEMBERSHIPS,
    EXPECTED_PEER_METRICS,
    EXPECTED_PERCENTILE_ROWS,
    EXPECTED_RADAR_METRICS,
    EXPECTED_UNIVERSE,
    audit_core_database,
    audit_peer_percentiles,
    audit_radar,
    audit_scoring,
    audit_source_limitations,
    run_sprint3_audit,
    table_exists,
)


# ============================================================
# EXPECTED CONFIGURATION
# ============================================================

def test_expected_universe():
    assert EXPECTED_UNIVERSE == 92


def test_expected_broad_sectors():
    assert EXPECTED_BROAD_SECTORS == 10


def test_expected_peer_groups():
    assert EXPECTED_PEER_GROUPS == 11


def test_expected_peer_memberships():
    assert EXPECTED_PEER_MEMBERSHIPS == 56


def test_expected_peer_metrics():
    assert EXPECTED_PEER_METRICS == 15


def test_expected_percentile_rows():
    assert EXPECTED_PERCENTILE_ROWS == 840


def test_expected_benchmarks():
    assert EXPECTED_BENCHMARKS == 11


def test_expected_radar_metrics():
    assert EXPECTED_RADAR_METRICS == 6


# ============================================================
# CORE DATABASE
# ============================================================

def test_required_tables_exist():
    connection = sqlite3.connect(
        "nifty100.db"
    )

    try:
        assert table_exists(
            connection,
            "companies",
        )

        assert table_exists(
            connection,
            "sectors",
        )

        assert table_exists(
            connection,
            "peer_percentiles",
        )

    finally:
        connection.close()


def test_core_database_audit_passes():
    connection = sqlite3.connect(
        "nifty100.db"
    )

    try:
        checks = audit_core_database(
            connection
        )

        assert checks

        assert all(
            check["passed"]
            for check in checks
        )

    finally:
        connection.close()


def test_company_universe_is_92():
    connection = sqlite3.connect(
        "nifty100.db"
    )

    try:
        count = connection.execute(
            """
            SELECT COUNT(*)
            FROM companies
            """
        ).fetchone()[0]

        assert count == 92

    finally:
        connection.close()


def test_no_duplicate_company_ids():
    connection = sqlite3.connect(
        "nifty100.db"
    )

    try:
        count = connection.execute(
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

        assert count == 0

    finally:
        connection.close()


def test_ten_broad_sectors():
    connection = sqlite3.connect(
        "nifty100.db"
    )

    try:
        count = connection.execute(
            """
            SELECT COUNT(
                DISTINCT broad_sector
            )
            FROM sectors
            WHERE broad_sector IS NOT NULL
            """
        ).fetchone()[0]

        assert count == 10

    finally:
        connection.close()


# ============================================================
# DAY 17 SCORING
# ============================================================

def test_scoring_audit_passes():
    checks = audit_scoring()

    assert checks

    assert all(
        check["passed"]
        for check in checks
    )


def test_scoring_has_three_audit_checks():
    checks = audit_scoring()

    assert len(checks) == 3


def test_scoring_weight_total_is_one():
    checks = audit_scoring()

    check = next(
        item
        for item in checks
        if item["name"]
        == "scoring weight total"
    )

    assert check["actual"] == 1.0
    assert check["passed"]


# ============================================================
# DAY 18 PEER ANALYTICS
# ============================================================

def test_peer_percentile_audit_passes():
    connection = sqlite3.connect(
        "nifty100.db"
    )

    try:
        checks = audit_peer_percentiles(
            connection
        )

        assert checks

        assert all(
            check["passed"]
            for check in checks
        )

    finally:
        connection.close()


def test_peer_percentile_row_count():
    connection = sqlite3.connect(
        "nifty100.db"
    )

    try:
        count = connection.execute(
            """
            SELECT COUNT(*)
            FROM peer_percentiles
            """
        ).fetchone()[0]

        assert count == 840

    finally:
        connection.close()


def test_peer_group_count():
    connection = sqlite3.connect(
        "nifty100.db"
    )

    try:
        count = connection.execute(
            """
            SELECT COUNT(
                DISTINCT peer_group_name
            )
            FROM peer_percentiles
            """
        ).fetchone()[0]

        assert count == 11

    finally:
        connection.close()


def test_peer_membership_count():
    connection = sqlite3.connect(
        "nifty100.db"
    )

    try:
        count = connection.execute(
            """
            SELECT COUNT(*)
            FROM (
                SELECT DISTINCT
                    peer_group_name,
                    company_id
                FROM peer_percentiles
            )
            """
        ).fetchone()[0]

        assert count == 56

    finally:
        connection.close()


def test_peer_metric_count():
    connection = sqlite3.connect(
        "nifty100.db"
    )

    try:
        count = connection.execute(
            """
            SELECT COUNT(
                DISTINCT metric
            )
            FROM peer_percentiles
            """
        ).fetchone()[0]

        assert count == 15

    finally:
        connection.close()


def test_818_populated_percentiles():
    connection = sqlite3.connect(
        "nifty100.db"
    )

    try:
        count = connection.execute(
            """
            SELECT COUNT(*)
            FROM peer_percentiles
            WHERE percentile IS NOT NULL
            """
        ).fetchone()[0]

        assert count == 818

    finally:
        connection.close()


def test_22_missing_percentiles():
    connection = sqlite3.connect(
        "nifty100.db"
    )

    try:
        count = connection.execute(
            """
            SELECT COUNT(*)
            FROM peer_percentiles
            WHERE percentile IS NULL
            """
        ).fetchone()[0]

        assert count == 22

    finally:
        connection.close()


def test_percentiles_between_zero_and_100():
    connection = sqlite3.connect(
        "nifty100.db"
    )

    try:
        count = connection.execute(
            """
            SELECT COUNT(*)
            FROM peer_percentiles
            WHERE percentile IS NOT NULL
              AND (
                    percentile < 0
                    OR percentile > 100
                  )
            """
        ).fetchone()[0]

        assert count == 0

    finally:
        connection.close()


def test_missing_values_not_fabricated():
    connection = sqlite3.connect(
        "nifty100.db"
    )

    try:
        count = connection.execute(
            """
            SELECT COUNT(*)
            FROM peer_percentiles
            WHERE raw_value IS NULL
              AND percentile IS NOT NULL
            """
        ).fetchone()[0]

        assert count == 0

    finally:
        connection.close()


# ============================================================
# BENCHMARK INTEGRITY
# ============================================================

def test_eleven_benchmark_companies():
    connection = sqlite3.connect(
        "nifty100.db"
    )

    try:
        count = connection.execute(
            """
            SELECT COUNT(*)
            FROM (
                SELECT DISTINCT
                    peer_group_name,
                    company_id
                FROM peer_percentiles
                WHERE is_benchmark = 1
            )
            """
        ).fetchone()[0]

        assert count == 11

    finally:
        connection.close()


def test_one_benchmark_per_group():
    connection = sqlite3.connect(
        "nifty100.db"
    )

    try:
        rows = connection.execute(
            """
            SELECT
                peer_group_name,
                COUNT(
                    DISTINCT CASE
                        WHEN is_benchmark = 1
                        THEN company_id
                    END
                )
            FROM peer_percentiles
            GROUP BY peer_group_name
            """
        ).fetchall()

        assert len(rows) == 11

        for _, count in rows:
            assert count == 1

    finally:
        connection.close()


# ============================================================
# DAY 19 RADAR
# ============================================================

def test_radar_audit_passes():
    checks = audit_radar()

    assert checks

    assert all(
        check["passed"]
        for check in checks
    )


def test_radar_has_two_audit_checks():
    assert len(
        audit_radar()
    ) == 2


# ============================================================
# SOURCE LIMITATIONS
# ============================================================

def test_source_limitations_reported():
    connection = sqlite3.connect(
        "nifty100.db"
    )

    try:
        limitations = (
            audit_source_limitations(
                connection
            )
        )

        assert len(limitations) >= 3

    finally:
        connection.close()


def test_missing_percentile_limitation_reported():
    connection = sqlite3.connect(
        "nifty100.db"
    )

    try:
        limitations = (
            audit_source_limitations(
                connection
            )
        )

        assert any(
            "22 peer percentile"
            in limitation
            for limitation in limitations
        )

    finally:
        connection.close()


def test_56_company_peer_limitation_reported():
    connection = sqlite3.connect(
        "nifty100.db"
    )

    try:
        limitations = (
            audit_source_limitations(
                connection
            )
        )

        assert any(
            "56" in limitation
            and "92" in limitation
            for limitation in limitations
        )

    finally:
        connection.close()


def test_fcf_source_limitation_reported():
    connection = sqlite3.connect(
        "nifty100.db"
    )

    try:
        limitations = (
            audit_source_limitations(
                connection
            )
        )

        assert any(
            "free cash flow"
            in limitation.lower()
            and "capex"
            in limitation.lower()
            for limitation in limitations
        )

    finally:
        connection.close()


# ============================================================
# COMPLETE SPRINT 3 AUDIT
# ============================================================

def test_complete_audit_passes():
    result = run_sprint3_audit()

    assert result[
        "status"
    ] == "PASS"


def test_complete_audit_has_23_checks():
    result = run_sprint3_audit()

    assert result[
        "total_checks"
    ] == 23


def test_complete_audit_23_passed():
    result = run_sprint3_audit()

    assert result[
        "passed"
    ] == 23


def test_complete_audit_zero_failed():
    result = run_sprint3_audit()

    assert result[
        "failed"
    ] == 0


def test_every_final_check_passed():
    result = run_sprint3_audit()

    assert all(
        check["passed"]
        for check in result[
            "checks"
        ]
    )