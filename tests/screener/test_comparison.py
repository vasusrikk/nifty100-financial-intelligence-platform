import pytest

from src.screener.comparison import (
    COMPARISON_METRICS,
    METRIC_LABELS,
    build_company_index,
    compare_companies,
    compare_metric_values,
    get_company,
)
from src.screener.engine import load_screener_data


# ============================================================
# CONFIGURATION
# ============================================================

def test_fifteen_comparison_metrics():
    assert len(COMPARISON_METRICS) == 15


def test_all_metrics_have_labels():
    for metric in COMPARISON_METRICS:
        assert metric in METRIC_LABELS


def test_metric_labels_not_empty():
    for metric in COMPARISON_METRICS:
        assert METRIC_LABELS[metric]


# ============================================================
# COMPANY INDEX / LOOKUP
# ============================================================

def test_company_index_unique():
    rows = load_screener_data()

    index = build_company_index(rows)

    assert len(index) == len(rows)


def test_get_company():
    company = get_company("TCS")

    assert company["company_id"] == "TCS"


def test_get_company_case_insensitive():
    company = get_company("tcs")

    assert company["company_id"] == "TCS"


def test_get_company_whitespace():
    company = get_company("  TCS  ")

    assert company["company_id"] == "TCS"


def test_unknown_company():
    with pytest.raises(ValueError):
        get_company(
            "NOT_A_REAL_COMPANY"
        )


# ============================================================
# INPUT VALIDATION
# ============================================================

def test_company_ids_must_be_list():
    with pytest.raises(ValueError):
        compare_companies("TCS")


def test_minimum_two_companies():
    with pytest.raises(ValueError):
        compare_companies(
            ["TCS"]
        )


def test_maximum_five_companies():
    with pytest.raises(ValueError):
        compare_companies(
            [
                "TCS",
                "INFY",
                "HCLTECH",
                "WIPRO",
                "LTIM",
                "TECHM",
            ]
        )


def test_duplicate_companies_rejected():
    with pytest.raises(ValueError):
        compare_companies(
            [
                "TCS",
                "tcs",
            ]
        )


# ============================================================
# METRIC COMPARISON
# ============================================================

def test_compare_metric_values():
    rows = load_screener_data()

    companies = [
        get_company("TCS", rows),
        get_company("INFY", rows),
    ]

    result = compare_metric_values(
        companies,
        "roe_pct",
    )

    assert len(result) == 2

    assert (
        result[0]["company_id"]
        == "TCS"
    )

    assert result[0]["value"] is not None


def test_invalid_comparison_metric():
    rows = load_screener_data()

    companies = [
        get_company("TCS", rows),
        get_company("INFY", rows),
    ]

    with pytest.raises(ValueError):
        compare_metric_values(
            companies,
            "fake_metric",
        )


# ============================================================
# FULL COMPARISON
# ============================================================

def test_three_company_comparison():
    output = compare_companies(
        [
            "TCS",
            "INFY",
            "HCLTECH",
        ]
    )

    assert output["company_count"] == 3

    assert len(
        output["companies"]
    ) == 3

    assert len(
        output["metrics"]
    ) == 15


def test_comparison_preserves_order():
    output = compare_companies(
        [
            "INFY",
            "TCS",
            "HCLTECH",
        ]
    )

    ids = [
        company["company_id"]
        for company in output[
            "companies"
        ]
    ]

    assert ids == [
        "INFY",
        "TCS",
        "HCLTECH",
    ]


def test_company_identity_fields():
    output = compare_companies(
        [
            "TCS",
            "INFY",
        ]
    )

    for company in output[
        "companies"
    ]:

        assert company[
            "company_id"
        ]

        assert company[
            "company_name"
        ]

        assert company[
            "year"
        ]

        assert company[
            "broad_sector"
        ]


def test_all_company_metrics_present():
    output = compare_companies(
        [
            "TCS",
            "INFY",
        ]
    )

    for company in output[
        "companies"
    ]:

        assert set(
            company["metrics"].keys()
        ) == set(
            COMPARISON_METRICS
        )


# ============================================================
# PERIOD ALIGNMENT
# ============================================================

def test_it_comparison_period():
    output = compare_companies(
        [
            "TCS",
            "INFY",
            "HCLTECH",
        ]
    )

    for company in output[
        "companies"
    ]:
        assert (
            company["year"]
            == "2024-03"
        )


# ============================================================
# DAY 17 SCORE INTEGRATION
# ============================================================

def test_composite_scores_present():
    output = compare_companies(
        [
            "TCS",
            "INFY",
            "HCLTECH",
        ]
    )

    for company in output[
        "companies"
    ]:

        assert (
            company[
                "composite_score"
            ]
            is not None
        )

        assert (
            0
            <= company[
                "composite_score"
            ]
            <= 100
        )


def test_score_coverage_present():
    output = compare_companies(
        [
            "TCS",
            "INFY",
            "HCLTECH",
        ]
    )

    for company in output[
        "companies"
    ]:

        assert (
            0
            <= company[
                "score_coverage_pct"
            ]
            <= 100
        )


def test_tcs_score_consistent():
    output = compare_companies(
        [
            "TCS",
            "INFY",
        ]
    )

    tcs = next(
        company
        for company in output[
            "companies"
        ]
        if company[
            "company_id"
        ] == "TCS"
    )

    assert (
        tcs["composite_score"]
        == pytest.approx(
            44.48,
            abs=0.01,
        )
    )


# ============================================================
# DATA INTEGRITY
# ============================================================

def test_comparison_does_not_modify_universe():
    rows = load_screener_data()

    original_count = len(rows)

    compare_companies(
        [
            "TCS",
            "INFY",
        ],
        rows=rows,
    )

    assert len(rows) == original_count


def test_comparison_company_ids_unique():
    output = compare_companies(
        [
            "TCS",
            "INFY",
            "HCLTECH",
        ]
    )

    ids = [
        company["company_id"]
        for company in output[
            "companies"
        ]
    ]

    assert len(ids) == len(set(ids))