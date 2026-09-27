import pytest

from src.screener.custom_screener import (
    VALID_OPERATORS,
    explain_match,
    run_custom_screener,
    validate_custom_filter,
    validate_custom_filters,
)
from src.screener.engine import load_screener_data


# ============================================================
# VALIDATION
# ============================================================

def test_valid_operators():
    assert VALID_OPERATORS == {
        ">",
        ">=",
        "<",
        "<=",
        "==",
        "!=",
    }


def test_valid_filter():
    result = validate_custom_filter(
        {
            "metric": "roe_pct",
            "operator": ">",
            "value": 15,
        }
    )

    assert result == {
        "metric": "roe_pct",
        "operator": ">",
        "value": 15.0,
    }


def test_numeric_string_value():
    result = validate_custom_filter(
        {
            "metric": "roe_pct",
            "operator": ">",
            "value": "15",
        }
    )

    assert result["value"] == 15.0


def test_filter_must_be_dictionary():
    with pytest.raises(ValueError):
        validate_custom_filter(
            "roe_pct > 15"
        )


def test_unsupported_metric():
    with pytest.raises(ValueError):
        validate_custom_filter(
            {
                "metric": "fake_metric",
                "operator": ">",
                "value": 10,
            }
        )


def test_invalid_operator():
    with pytest.raises(ValueError):
        validate_custom_filter(
            {
                "metric": "roe_pct",
                "operator": "BETWEEN",
                "value": 10,
            }
        )


def test_missing_value():
    with pytest.raises(ValueError):
        validate_custom_filter(
            {
                "metric": "roe_pct",
                "operator": ">",
                "value": None,
            }
        )


def test_non_numeric_value():
    with pytest.raises(ValueError):
        validate_custom_filter(
            {
                "metric": "roe_pct",
                "operator": ">",
                "value": "high",
            }
        )


def test_filters_must_be_list():
    with pytest.raises(ValueError):
        validate_custom_filters(
            {
                "metric": "roe_pct",
                "operator": ">",
                "value": 15,
            }
        )


def test_empty_filters_rejected():
    with pytest.raises(ValueError):
        validate_custom_filters([])


# ============================================================
# CUSTOM SCREEN EXECUTION
# ============================================================

def test_custom_screen_runs():
    output = run_custom_screener(
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

    assert output["total_universe"] == 92
    assert output["matched_count"] == 33
    assert output["ranked"] is True


def test_results_have_ranks():
    output = run_custom_screener(
        [
            {
                "metric": "roe_pct",
                "operator": ">",
                "value": 15,
            }
        ]
    )

    for row in output["results"]:
        assert "rank" in row
        assert "composite_score" in row


def test_unranked_results():
    output = run_custom_screener(
        [
            {
                "metric": "roe_pct",
                "operator": ">",
                "value": 15,
            }
        ],
        rank_results=False,
    )

    assert output["ranked"] is False


def test_limit():
    output = run_custom_screener(
        [
            {
                "metric": "roe_pct",
                "operator": ">",
                "value": 15,
            }
        ],
        limit=5,
    )

    assert len(output["results"]) == 5
    assert output["matched_count"] == 5


def test_invalid_limit():
    with pytest.raises(ValueError):
        run_custom_screener(
            [
                {
                    "metric": "roe_pct",
                    "operator": ">",
                    "value": 15,
                }
            ],
            limit="invalid",
        )


def test_zero_limit_rejected():
    with pytest.raises(ValueError):
        run_custom_screener(
            [
                {
                    "metric": "roe_pct",
                    "operator": ">",
                    "value": 15,
                }
            ],
            limit=0,
        )


# ============================================================
# AND LOGIC
# ============================================================

def test_multiple_filters_use_and_logic():
    output = run_custom_screener(
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
        rank_results=False,
    )

    for row in output["results"]:
        assert row["roe_pct"] > 15
        assert (
            row["revenue_cagr_5yr"]
            > 10
        )


# ============================================================
# FINANCIAL-SECTOR CARVE-OUT
# ============================================================

def test_financial_de_carveout_preserved():
    output = run_custom_screener(
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
        for row in output["results"]
    }

    # These financial companies have D/E > 1,
    # but the Day 15 financial-sector carve-out
    # deliberately exempts them from generic D/E filtering.
    assert "ICICIBANK" in result_by_id
    assert (
        result_by_id[
            "ICICIBANK"
        ]["de_ratio"]
        > 1
    )


# ============================================================
# EXPLANATION
# ============================================================

def test_explain_match():
    rows = load_screener_data()

    abb = next(
        row
        for row in rows
        if row["company_id"] == "ABB"
    )

    filters = [
        {
            "metric": "roe_pct",
            "operator": ">",
            "value": 15.0,
        }
    ]

    explanation = explain_match(
        abb,
        filters,
    )

    assert len(explanation) == 1
    assert (
        explanation[0]["metric"]
        == "roe_pct"
    )

    assert (
        explanation[0]["actual"]
        == abb["roe_pct"]
    )


# ============================================================
# RESULT INTEGRITY
# ============================================================

def test_rank_sequence_after_filtering():
    output = run_custom_screener(
        [
            {
                "metric": "roe_pct",
                "operator": ">",
                "value": 15,
            }
        ]
    )

    ranks = [
        row["rank"]
        for row in output["results"]
    ]

    assert ranks == list(
        range(
            1,
            len(ranks) + 1,
        )
    )


def test_company_ids_unique():
    output = run_custom_screener(
        [
            {
                "metric": "roe_pct",
                "operator": ">",
                "value": 0,
            }
        ]
    )

    company_ids = [
        row["company_id"]
        for row in output["results"]
    ]

    assert len(company_ids) == len(
        set(company_ids)
    )