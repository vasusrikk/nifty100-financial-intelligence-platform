import pytest

from src.screener.engine import load_screener_data
from src.screener.scoring import (
    SCORING_WEIGHTS,
    LOWER_IS_BETTER,
    get_winsor_bounds,
    normalize_value,
    percentile,
    prepare_metric_bounds,
    rank_companies,
    score_company,
    score_metric,
    valid_number,
    winsorize_value,
)


# ============================================================
# SCORING CONFIGURATION
# ============================================================

def test_scoring_weight_total():
    assert sum(
        SCORING_WEIGHTS.values()
    ) == pytest.approx(1.0)


def test_eight_scoring_metrics():
    assert len(SCORING_WEIGHTS) == 8


def test_de_ratio_lower_is_better():
    assert "de_ratio" in LOWER_IS_BETTER


# ============================================================
# NUMERIC VALIDATION
# ============================================================

def test_valid_numbers():
    assert valid_number(10)
    assert valid_number(10.5)
    assert valid_number("20")


def test_invalid_numbers():
    assert not valid_number(None)
    assert not valid_number("abc")
    assert not valid_number(float("nan"))
    assert not valid_number(float("inf"))


# ============================================================
# PERCENTILE
# ============================================================

def test_percentile_basic():
    values = [
        10,
        20,
        30,
        40,
        50,
    ]

    assert percentile(
        values,
        50,
    ) == 30


def test_percentile_empty():
    assert percentile(
        [],
        50,
    ) is None


# ============================================================
# WINSORISATION
# ============================================================

def test_winsorize_upper_extreme():
    result = winsorize_value(
        1000,
        10,
        100,
    )

    assert result == 100


def test_winsorize_lower_extreme():
    result = winsorize_value(
        -100,
        0,
        100,
    )

    assert result == 0


def test_winsorize_normal_value():
    result = winsorize_value(
        50,
        0,
        100,
    )

    assert result == 50


def test_winsorize_missing():
    assert winsorize_value(
        None,
        0,
        100,
    ) is None


# ============================================================
# NORMALIZATION
# ============================================================

def test_higher_is_better_normalization():
    assert normalize_value(
        75,
        0,
        100,
        True,
    ) == 75


def test_lower_is_better_normalization():
    assert normalize_value(
        25,
        0,
        100,
        False,
    ) == 75


def test_normalization_bounds():
    assert normalize_value(
        200,
        0,
        100,
        True,
    ) == 100

    assert normalize_value(
        -100,
        0,
        100,
        True,
    ) == 0


def test_equal_min_max():
    assert normalize_value(
        10,
        10,
        10,
        True,
    ) == 50


# ============================================================
# REAL DATABASE OUTLIER CONTROL
# ============================================================

def test_roe_outlier_is_winsorized():
    rows = load_screener_data()

    raw_max = max(
        row["roe_pct"]
        for row in rows
        if valid_number(
            row.get("roe_pct")
        )
    )

    lower, upper = get_winsor_bounds(
        rows,
        "roe_pct",
    )

    assert raw_max > 1000
    assert upper < raw_max
    assert upper < 100


def test_bel_roe_score_is_bounded():
    rows = load_screener_data()

    bounds = prepare_metric_bounds(
        rows
    )

    bel = next(
        row
        for row in rows
        if row["company_id"] == "BEL"
    )

    score = score_metric(
        bel["roe_pct"],
        "roe_pct",
        bounds,
    )

    assert 0 <= score <= 100
    assert score == 100


# ============================================================
# COMPANY SCORING
# ============================================================

def test_company_composite_score_bounds():
    rows = load_screener_data()

    bounds = prepare_metric_bounds(
        rows
    )

    for row in rows:

        result = score_company(
            row,
            bounds,
        )

        score = result[
            "composite_score"
        ]

        if score is not None:
            assert 0 <= score <= 100


def test_metric_scores_are_bounded():
    rows = load_screener_data()

    bounds = prepare_metric_bounds(
        rows
    )

    for row in rows[:20]:

        result = score_company(
            row,
            bounds,
        )

        for score in (
            result[
                "metric_scores"
            ].values()
        ):
            if score is not None:
                assert 0 <= score <= 100


# ============================================================
# MISSING DATA
# ============================================================

def test_missing_metric_not_scored_as_zero():
    rows = load_screener_data()

    bounds = prepare_metric_bounds(
        rows
    )

    test_row = dict(rows[0])

    test_row["roe_pct"] = None

    result = score_company(
        test_row,
        bounds,
    )

    assert (
        result["metric_scores"][
            "roe_pct"
        ]
        is None
    )


def test_missing_metric_reduces_coverage():
    rows = load_screener_data()

    bounds = prepare_metric_bounds(
        rows
    )

    test_row = dict(rows[0])

    test_row["roe_pct"] = None

    result = score_company(
        test_row,
        bounds,
    )

    assert (
        result["score_coverage_pct"]
        < 100
    )


def test_all_metrics_missing():
    rows = load_screener_data()

    bounds = prepare_metric_bounds(
        rows
    )

    test_row = {
        "company_id": "TEST",
    }

    result = score_company(
        test_row,
        bounds,
    )

    assert (
        result["composite_score"]
        is None
    )

    assert (
        result["score_coverage_pct"]
        == 0
    )


# ============================================================
# RANKING
# ============================================================

def test_all_real_companies_ranked():
    rows = load_screener_data()

    ranked = rank_companies(
        rows
    )

    assert len(ranked) == len(rows)


def test_rank_numbers_unique():
    ranked = rank_companies()

    ranks = [
        row["rank"]
        for row in ranked
    ]

    assert len(ranks) == len(
        set(ranks)
    )


def test_rank_sequence():
    ranked = rank_companies()

    ranks = [
        row["rank"]
        for row in ranked
    ]

    assert ranks == list(
        range(
            1,
            len(ranked) + 1,
        )
    )


def test_scores_descending():
    ranked = rank_companies()

    scores = [
        row["composite_score"]
        for row in ranked
    ]

    assert scores == sorted(
        scores,
        reverse=True,
    )


def test_ranking_deterministic():
    first = rank_companies()
    second = rank_companies()

    first_order = [
        row["company_id"]
        for row in first
    ]

    second_order = [
        row["company_id"]
        for row in second
    ]

    assert first_order == second_order


def test_top_rank_exists():
    ranked = rank_companies()

    assert ranked[0]["rank"] == 1
    assert (
        ranked[0]["composite_score"]
        is not None
    )