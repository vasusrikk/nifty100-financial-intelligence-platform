"""Tests for Original Sprint 3 - Day 19 radar charts."""

import sqlite3
from pathlib import Path

from src.analytics.radar import (
    RADAR_METRICS,
    build_company_profiles,
    calculate_peer_medians,
    generate_all_radar_charts,
    generate_radar_chart,
    get_profile_values,
    load_radar_data,
    prepare_plot_values,
    safe_filename,
)


# ============================================================
# CONFIGURATION
# ============================================================

def test_radar_metric_count():
    assert len(RADAR_METRICS) == 6


def test_expected_radar_metrics():
    metrics = {
        metric
        for metric, _ in RADAR_METRICS
    }

    assert metrics == {
        "roe_pct",
        "roce_pct",
        "revenue_cagr_5yr",
        "pat_cagr_5yr",
        "cfo_margin_pct",
        "pe_ratio",
    }


def test_radar_labels_unique():
    labels = [
        label
        for _, label in RADAR_METRICS
    ]

    assert len(labels) == len(
        set(labels)
    )


# ============================================================
# LOAD DAY 18 DATA
# ============================================================

def test_radar_data_loaded():
    rows = load_radar_data()

    assert len(rows) > 0


def test_radar_data_has_11_groups():
    rows = load_radar_data()

    groups = {
        row[0]
        for row in rows
    }

    assert len(groups) == 11


def test_radar_data_has_56_companies():
    rows = load_radar_data()

    companies = {
        (
            row[0],
            row[1],
        )
        for row in rows
    }

    assert len(companies) == 56


def test_radar_database_metrics():
    rows = load_radar_data()

    metrics = {
        row[4]
        for row in rows
    }

    assert metrics == {
        metric
        for metric, _ in RADAR_METRICS
    }


# ============================================================
# COMPANY PROFILES
# ============================================================

def test_build_56_profiles():
    rows = load_radar_data()

    profiles = build_company_profiles(
        rows
    )

    assert len(profiles) == 56


def test_profile_has_required_fields():
    rows = load_radar_data()

    profiles = build_company_profiles(
        rows
    )

    profile = profiles[0]

    assert "peer_group_name" in profile
    assert "company_id" in profile
    assert "company_name" in profile
    assert "is_benchmark" in profile
    assert "year" in profile
    assert "metrics" in profile


def test_each_profile_has_six_metrics():
    rows = load_radar_data()

    profiles = build_company_profiles(
        rows
    )

    for profile in profiles:
        assert len(
            profile["metrics"]
        ) == 6


def test_profile_values_length():
    rows = load_radar_data()

    profiles = build_company_profiles(
        rows
    )

    for profile in profiles:
        values = get_profile_values(
            profile
        )

        assert len(values) == 6


def test_profile_percentiles_valid():
    rows = load_radar_data()

    profiles = build_company_profiles(
        rows
    )

    for profile in profiles:

        for value in get_profile_values(
            profile
        ):
            if value is not None:
                assert 0 <= value <= 100


# ============================================================
# BENCHMARKS
# ============================================================

def test_11_benchmark_profiles():
    rows = load_radar_data()

    profiles = build_company_profiles(
        rows
    )

    benchmarks = [
        profile
        for profile in profiles
        if profile["is_benchmark"]
    ]

    assert len(benchmarks) == 11


def test_one_benchmark_per_group():
    rows = load_radar_data()

    profiles = build_company_profiles(
        rows
    )

    groups = {}

    for profile in profiles:

        group = profile[
            "peer_group_name"
        ]

        groups.setdefault(
            group,
            0,
        )

        if profile["is_benchmark"]:
            groups[group] += 1

    assert len(groups) == 11

    for count in groups.values():
        assert count == 1


# ============================================================
# PEER MEDIANS
# ============================================================

def test_peer_medians_have_11_groups():
    rows = load_radar_data()

    profiles = build_company_profiles(
        rows
    )

    medians = calculate_peer_medians(
        profiles
    )

    assert len(medians) == 11


def test_each_peer_median_has_six_values():
    rows = load_radar_data()

    profiles = build_company_profiles(
        rows
    )

    medians = calculate_peer_medians(
        profiles
    )

    for values in medians.values():
        assert len(values) == 6


def test_peer_median_range():
    rows = load_radar_data()

    profiles = build_company_profiles(
        rows
    )

    medians = calculate_peer_medians(
        profiles
    )

    for values in medians.values():

        for value in values:
            if value is not None:
                assert 0 <= value <= 100


# ============================================================
# MISSING VALUES
# ============================================================

def test_verified_missing_radar_values():
    rows = load_radar_data()

    profiles = build_company_profiles(
        rows
    )

    missing = sum(
        value is None
        for profile in profiles
        for value in get_profile_values(
            profile
        )
    )

    # Current verified Day 19 source-data result.
    assert missing == 10


def test_prepare_plot_values_preserves_length():
    values = [
        100,
        None,
        50,
        25,
        None,
        75,
    ]

    result = prepare_plot_values(
        values
    )

    assert len(result) == 6


def test_prepare_plot_values_converts_missing():
    values = [
        100,
        None,
        50,
    ]

    result = prepare_plot_values(
        values
    )

    assert result == [
        100.0,
        0.0,
        50.0,
    ]


# ============================================================
# FILENAMES
# ============================================================

def test_safe_filename_normal():
    assert safe_filename(
        "HDFCBANK"
    ) == "HDFCBANK"


def test_safe_filename_special_characters():
    assert safe_filename(
        "ABC/TEST:1"
    ) == "ABC_TEST_1"


# ============================================================
# SINGLE PNG GENERATION
# ============================================================

def test_generate_single_radar_png(
    tmp_path,
):
    rows = load_radar_data()

    profiles = build_company_profiles(
        rows
    )

    medians = calculate_peer_medians(
        profiles
    )

    profile = profiles[0]

    output = generate_radar_chart(
        profile,
        medians[
            profile[
                "peer_group_name"
            ]
        ],
        output_dir=tmp_path,
    )

    assert output.exists()
    assert output.suffix == ".png"
    assert output.stat().st_size > 0


# ============================================================
# COMPLETE PIPELINE
# ============================================================

def test_generate_all_radar_charts(
    tmp_path,
):
    result = generate_all_radar_charts(
        output_dir=tmp_path
    )

    assert result[
        "peer_groups"
    ] == 11

    assert result[
        "company_count"
    ] == 56

    assert result[
        "chart_count"
    ] == 56


def test_all_generated_files_exist(
    tmp_path,
):
    result = generate_all_radar_charts(
        output_dir=tmp_path
    )

    assert len(
        result["charts"]
    ) == 56

    for path in result["charts"]:
        assert path.exists()


def test_all_generated_files_are_png(
    tmp_path,
):
    result = generate_all_radar_charts(
        output_dir=tmp_path
    )

    for path in result["charts"]:
        assert path.suffix.lower() == ".png"


def test_all_generated_pngs_nonempty(
    tmp_path,
):
    result = generate_all_radar_charts(
        output_dir=tmp_path
    )

    for path in result["charts"]:
        assert path.stat().st_size > 0


def test_generated_company_ids_unique(
    tmp_path,
):
    result = generate_all_radar_charts(
        output_dir=tmp_path
    )

    stems = [
        path.stem
        for path in result["charts"]
    ]

    assert len(stems) == len(
        set(stems)
    )


# ============================================================
# SOURCE DATABASE INTEGRITY
# ============================================================

def test_peer_percentiles_still_840():
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


def test_radar_generation_does_not_change_peer_table(
    tmp_path,
):
    connection = sqlite3.connect(
        "nifty100.db"
    )

    try:
        before = connection.execute(
            """
            SELECT COUNT(*)
            FROM peer_percentiles
            """
        ).fetchone()[0]

    finally:
        connection.close()

    generate_all_radar_charts(
        output_dir=tmp_path
    )

    connection = sqlite3.connect(
        "nifty100.db"
    )

    try:
        after = connection.execute(
            """
            SELECT COUNT(*)
            FROM peer_percentiles
            """
        ).fetchone()[0]

    finally:
        connection.close()

    assert before == after == 840