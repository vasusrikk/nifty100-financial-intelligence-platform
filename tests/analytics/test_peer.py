"""Tests for Original Sprint 3 - Day 18 peer percentile analytics."""

import sqlite3

import pytest

from src.analytics.peer import (
    EXPECTED_PEER_GROUP_COUNT,
    PEER_METRICS,
    build_peer_percentiles,
    calculate_peer_percentiles,
    group_peer_memberships,
    load_peer_groups,
    percent_rank,
    validate_company_ids,
    validate_peer_groups,
)


# ============================================================
# PEER-GROUP SOURCE FILE
# ============================================================

def test_peer_group_count():
    memberships = load_peer_groups()
    groups = group_peer_memberships(
        memberships
    )

    assert len(groups) == 11
    assert (
        len(groups)
        == EXPECTED_PEER_GROUP_COUNT
    )


def test_membership_count():
    memberships = load_peer_groups()

    assert len(memberships) == 56


def test_expected_peer_group_names():
    memberships = load_peer_groups()
    groups = group_peer_memberships(
        memberships
    )

    assert set(groups) == {
        "Private Banks",
        "Public Sector Banks",
        "IT Services",
        "Pharmaceuticals",
        "Automobiles",
        "Life Insurance",
        "Oil & Gas",
        "Power & Utilities",
        "Steel",
        "FMCG",
        "Consumer Finance",
    }


def test_exactly_one_benchmark_per_group():
    memberships = load_peer_groups()

    groups = validate_peer_groups(
        memberships
    )

    for members in groups.values():
        benchmarks = [
            row
            for row in members
            if row["is_benchmark"]
        ]

        assert len(benchmarks) == 1


def test_known_benchmarks():
    memberships = load_peer_groups()
    groups = validate_peer_groups(
        memberships
    )

    expected = {
        "Private Banks": "HDFCBANK",
        "Public Sector Banks": "SBIN",
        "IT Services": "TCS",
        "Pharmaceuticals": "SUNPHARMA",
        "Automobiles": "MARUTI",
        "Life Insurance": "LICI",
        "Oil & Gas": "RELIANCE",
        "Power & Utilities": "NTPC",
        "Steel": "TATASTEEL",
        "FMCG": "HINDUNILVR",
        "Consumer Finance": "BAJFINANCE",
    }

    for group_name, benchmark in (
        expected.items()
    ):
        actual = next(
            row["company_id"]
            for row in groups[group_name]
            if row["is_benchmark"]
        )

        assert actual == benchmark


# ============================================================
# DATABASE MEMBERSHIP VALIDATION
# ============================================================

def test_all_peer_companies_exist():
    memberships = load_peer_groups()

    connection = sqlite3.connect(
        "nifty100.db"
    )

    try:
        assert validate_company_ids(
            connection,
            memberships,
        )
    finally:
        connection.close()


# ============================================================
# METRIC CONFIGURATION
# ============================================================

def test_peer_metric_count():
    assert len(PEER_METRICS) == 15


def test_de_is_lower_is_better():
    assert PEER_METRICS[
        "de_ratio"
    ] is False


def test_pe_is_lower_is_better():
    assert PEER_METRICS[
        "pe_ratio"
    ] is False


def test_pb_is_lower_is_better():
    assert PEER_METRICS[
        "pb_ratio"
    ] is False


def test_roe_is_higher_is_better():
    assert PEER_METRICS[
        "roe_pct"
    ] is True


# ============================================================
# PERCENT_RANK BEHAVIOUR
# ============================================================

def test_percent_rank_higher_is_better():
    values = {
        "A": 30,
        "B": 20,
        "C": 10,
    }

    result = percent_rank(
        values,
        higher_is_better=True,
    )

    assert result["A"] == 100.0
    assert result["B"] == 50.0
    assert result["C"] == 0.0


def test_percent_rank_lower_is_better():
    values = {
        "A": 1,
        "B": 2,
        "C": 3,
    }

    result = percent_rank(
        values,
        higher_is_better=False,
    )

    assert result["A"] == 100.0
    assert result["B"] == 50.0
    assert result["C"] == 0.0


def test_percent_rank_ties():
    values = {
        "A": 30,
        "B": 30,
        "C": 10,
    }

    result = percent_rank(
        values,
        higher_is_better=True,
    )

    assert result["A"] == result["B"]
    assert result["A"] == 100.0
    assert result["C"] == 0.0


def test_percent_rank_single_value():
    result = percent_rank(
        {"A": 10},
        higher_is_better=True,
    )

    assert result == {
        "A": 100.0
    }


def test_percent_rank_ignores_missing():
    values = {
        "A": 30,
        "B": None,
        "C": 10,
    }

    result = percent_rank(values)

    assert "A" in result
    assert "C" in result
    assert "B" not in result


def test_percent_rank_empty():
    assert percent_rank({}) == {}


# ============================================================
# PIPELINE
# ============================================================

def test_complete_pipeline():
    result = build_peer_percentiles()

    assert result[
        "peer_groups"
    ] == 11

    assert result[
        "memberships"
    ] == 56

    assert result[
        "companies_with_financials"
    ] == 56

    assert result[
        "metrics"
    ] == 15

    assert result[
        "percentile_rows"
    ] == 840


def test_all_output_groups_present():
    result = build_peer_percentiles()

    groups = {
        row["peer_group_name"]
        for row in result["rows"]
    }

    assert len(groups) == 11


def test_all_output_companies_present():
    result = build_peer_percentiles()

    companies = {
        row["company_id"]
        for row in result["rows"]
    }

    assert len(companies) == 56


def test_each_membership_has_15_metrics():
    result = build_peer_percentiles()

    combinations = {}

    for row in result["rows"]:
        key = (
            row["peer_group_name"],
            row["company_id"],
        )

        combinations.setdefault(
            key,
            set(),
        ).add(
            row["metric"]
        )

    assert len(combinations) == 56

    for metrics in combinations.values():
        assert len(metrics) == 15


# ============================================================
# PERCENTILE QUALITY
# ============================================================

def test_percentiles_in_valid_range():
    result = build_peer_percentiles()

    for row in result["rows"]:
        value = row["percentile"]

        if value is not None:
            assert 0 <= value <= 100


def test_missing_raw_value_has_no_percentile():
    result = build_peer_percentiles()

    for row in result["rows"]:
        if row["raw_value"] is None:
            assert row[
                "percentile"
            ] is None


def test_populated_percentile_count():
    result = build_peer_percentiles()

    populated = sum(
        row["percentile"] is not None
        for row in result["rows"]
    )

    # Current verified source-data result.
    assert populated == 818


def test_missing_percentile_count():
    result = build_peer_percentiles()

    missing = sum(
        row["percentile"] is None
        for row in result["rows"]
    )

    # 840 theoretical rows - 818 populated.
    assert missing == 22


# ============================================================
# DATABASE TABLE
# ============================================================

def test_peer_percentiles_table_exists():
    build_peer_percentiles()

    connection = sqlite3.connect(
        "nifty100.db"
    )

    try:
        result = connection.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE
                type = 'table'
                AND name = 'peer_percentiles'
            """
        ).fetchone()

        assert result is not None

    finally:
        connection.close()


def test_peer_percentiles_database_count():
    build_peer_percentiles()

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


def test_database_has_11_groups():
    build_peer_percentiles()

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


def test_database_has_56_companies():
    build_peer_percentiles()

    connection = sqlite3.connect(
        "nifty100.db"
    )

    try:
        count = connection.execute(
            """
            SELECT COUNT(
                DISTINCT company_id
            )
            FROM peer_percentiles
            """
        ).fetchone()[0]

        assert count == 56

    finally:
        connection.close()


def test_database_has_15_metrics():
    build_peer_percentiles()

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


def test_one_benchmark_per_group_in_database():
    build_peer_percentiles()

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