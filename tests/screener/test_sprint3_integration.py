"""Sprint 3 - Day 21: End-to-End Integration Tests."""

import csv
import json

from src.screener.comparison import compare_companies
from src.screener.custom_screener import run_custom_screener
from src.screener.engine import (
    apply_filters,
    load_screener_data,
)
from src.screener.exporter import export_results
from src.screener.presets import run_preset
from src.screener.scoring import rank_companies


# ============================================================
# UNIVERSE INTEGRITY
# ============================================================

def test_sprint3_universe_integrity():
    rows = load_screener_data()

    assert len(rows) == 92

    company_ids = [
        row["company_id"]
        for row in rows
    ]

    assert len(company_ids) == len(
        set(company_ids)
    )


# ============================================================
# DAY 15 -> DAY 17
# FILTER -> RANKING PIPELINE
# ============================================================

def test_filter_to_ranking_pipeline():
    rows = load_screener_data()

    filtered = apply_filters(
        rows,
        [
            {
                "metric": "roe_pct",
                "operator": ">",
                "value": 15,
            },
            {
                "metric": "de_ratio",
                "operator": "<",
                "value": 1,
            },
        ],
    )

    ranked = rank_companies(
        filtered
    )

    assert len(filtered) > 0
    assert len(ranked) == len(filtered)

    assert [
        row["rank"]
        for row in ranked
    ] == list(
        range(
            1,
            len(ranked) + 1,
        )
    )


# ============================================================
# DAY 16 PRESET INTEGRATION
# ============================================================

def test_complete_preset_pipeline():
    result = run_preset(
        "value_pick"
    )

    assert result["status"] == "COMPLETE"

    assert len(
        result["results"]
    ) == 2


def test_source_limitation_preserved():
    result = run_preset(
        "quality_compounder"
    )

    assert (
        result["status"]
        == "SOURCE_LIMITATION"
    )

    assert (
        "FCF"
        in result["reason"]
    )


# ============================================================
# DAY 18 CUSTOM SCREEN INTEGRATION
# ============================================================

def test_custom_screen_full_pipeline():
    filters = [
        {
            "metric": "roe_pct",
            "operator": ">",
            "value": 15,
        },
        {
            "metric": "de_ratio",
            "operator": "<",
            "value": 1,
        },
        {
            "metric": "revenue_cagr_5yr",
            "operator": ">",
            "value": 10,
        },
    ]

    result = run_custom_screener(
        filters
    )

    assert result["total_universe"] == 92
    assert result["matched_count"] == 33
    assert result["ranked"] is True

    assert len(
        result["results"]
    ) == 33

    assert (
        result["results"][0]["rank"]
        == 1
    )


# ============================================================
# FINANCIAL-SECTOR RULE INTEGRATION
# ============================================================

def test_financial_de_carveout_end_to_end():
    result = run_custom_screener(
        [
            {
                "metric": "roe_pct",
                "operator": ">",
                "value": 15,
            },
            {
                "metric": "de_ratio",
                "operator": "<",
                "value": 1,
            },
            {
                "metric": "revenue_cagr_5yr",
                "operator": ">",
                "value": 10,
            },
        ],
        rank_results=False,
    )

    result_by_id = {
        row["company_id"]: row
        for row in result["results"]
    }

    assert "ICICIBANK" in result_by_id

    assert (
        result_by_id[
            "ICICIBANK"
        ]["de_ratio"]
        > 1
    )


# ============================================================
# DAY 17 OUTLIER CONTROL INTEGRATION
# ============================================================

def test_extreme_roe_does_not_break_scoring():
    ranked = rank_companies()

    bel = next(
        row
        for row in ranked
        if row["company_id"] == "BEL"
    )

    assert bel["roe_pct"] > 1000

    assert (
        0
        <= bel["composite_score"]
        <= 100
    )

    assert (
        bel["metric_scores"][
            "roe_pct"
        ]
        == 100
    )


# ============================================================
# DAY 19 COMPARISON INTEGRATION
# ============================================================

def test_comparison_pipeline():
    result = compare_companies(
        [
            "TCS",
            "INFY",
            "HCLTECH",
        ]
    )

    assert result["company_count"] == 3
    assert len(result["metrics"]) == 15

    ids = [
        company["company_id"]
        for company in result[
            "companies"
        ]
    ]

    assert ids == [
        "TCS",
        "INFY",
        "HCLTECH",
    ]

    for company in result["companies"]:
        assert (
            company["year"]
            == "2024-03"
        )

        assert (
            company[
                "composite_score"
            ]
            is not None
        )


# ============================================================
# CUSTOM SCREEN -> COMPARISON
# ============================================================

def test_screen_results_can_be_compared():
    screen = run_custom_screener(
        [
            {
                "metric": "roe_pct",
                "operator": ">",
                "value": 15,
            },
            {
                "metric": "revenue_cagr_5yr",
                "operator": ">",
                "value": 10,
            },
        ]
    )

    selected_ids = [
        row["company_id"]
        for row in screen[
            "results"
        ][:3]
    ]

    comparison = compare_companies(
        selected_ids
    )

    assert (
        comparison["company_count"]
        == 3
    )


# ============================================================
# DAY 20 CSV EXPORT INTEGRATION
# ============================================================

def test_screen_to_csv_export(
    tmp_path,
):
    screen = run_custom_screener(
        [
            {
                "metric": "roe_pct",
                "operator": ">",
                "value": 15,
            },
            {
                "metric": "de_ratio",
                "operator": "<",
                "value": 1,
            },
            {
                "metric": "revenue_cagr_5yr",
                "operator": ">",
                "value": 10,
            },
        ]
    )

    path = export_results(
        screen["results"],
        "integration_screen",
        "csv",
        tmp_path,
    )

    assert path.exists()

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        exported = list(
            csv.DictReader(file)
        )

    assert len(exported) == 33

    assert (
        exported[0]["company_id"]
        == screen[
            "results"
        ][0]["company_id"]
    )


# ============================================================
# DAY 20 JSON EXPORT INTEGRATION
# ============================================================

def test_ranked_universe_to_json(
    tmp_path,
):
    ranked = rank_companies()

    path = export_results(
        ranked,
        "integration_ranked",
        "json",
        tmp_path,
    )

    assert path.exists()

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:

        exported = json.load(file)

    assert len(exported) == 92

    assert (
        exported[0]["rank"]
        == 1
    )


# ============================================================
# FULL PIPELINE
# ============================================================

def test_complete_sprint3_pipeline(
    tmp_path,
):
    # 1. Load
    universe = load_screener_data()

    assert len(universe) == 92

    # 2. Custom screen
    screen = run_custom_screener(
        [
            {
                "metric": "roe_pct",
                "operator": ">",
                "value": 15,
            },
            {
                "metric": "revenue_cagr_5yr",
                "operator": ">",
                "value": 10,
            },
        ],
        rows=universe,
    )

    assert (
        screen["matched_count"]
        > 0
    )

    # 3. Ranked output
    results = screen["results"]

    assert results[0]["rank"] == 1

    # 4. Compare top companies
    top_ids = [
        row["company_id"]
        for row in results[:3]
    ]

    comparison = compare_companies(
        top_ids,
        rows=universe,
    )

    assert (
        comparison["company_count"]
        == 3
    )

    # 5. Export results
    export_path = export_results(
        results,
        "sprint3_final",
        "json",
        tmp_path,
    )

    assert export_path.exists()

    # 6. Verify exported data
    with export_path.open(
        "r",
        encoding="utf-8",
    ) as file:

        exported = json.load(file)

    assert len(exported) == len(
        results
    )

    assert (
        exported[0]["company_id"]
        == results[0]["company_id"]
    )


# ============================================================
# DETERMINISM
# ============================================================

def test_full_ranking_is_deterministic():
    first = rank_companies()
    second = rank_companies()

    assert [
        row["company_id"]
        for row in first
    ] == [
        row["company_id"]
        for row in second
    ]


# ============================================================
# RAW DATABASE VALUES REMAIN AVAILABLE
# ============================================================

def test_raw_extreme_value_preserved():
    rows = load_screener_data()

    bel = next(
        row
        for row in rows
        if row["company_id"] == "BEL"
    )

    # Winsorisation occurs only in scoring.
    # Raw source value must remain unchanged.
    assert bel["roe_pct"] > 1000