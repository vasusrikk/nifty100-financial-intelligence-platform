"""Sprint 3 - Day 18: Custom Screener."""

from __future__ import annotations

from src.screener.engine import (
    SUPPORTED_FILTERS,
    apply_filters,
    load_screener_data,
)
from src.screener.scoring import rank_companies


VALID_OPERATORS = {
    ">",
    ">=",
    "<",
    "<=",
    "==",
    "!=",
}


# ============================================================
# VALIDATION
# ============================================================

def validate_custom_filter(filter_item):
    """
    Validate one custom screener condition.
    """

    if not isinstance(filter_item, dict):
        raise ValueError(
            "Each filter must be a dictionary."
        )

    metric = filter_item.get("metric")
    operator = filter_item.get("operator")
    value = filter_item.get("value")

    if metric not in SUPPORTED_FILTERS:
        raise ValueError(
            f"Unsupported filter metric: {metric}"
        )

    if operator not in VALID_OPERATORS:
        raise ValueError(
            f"Unsupported operator: {operator}"
        )

    if value is None:
        raise ValueError(
            f"Filter value is required for {metric}."
        )

    try:
        numeric_value = float(value)
    except (TypeError, ValueError):
        raise ValueError(
            f"Filter value for {metric} must be numeric."
        )

    return {
        "metric": metric,
        "operator": operator,
        "value": numeric_value,
    }


def validate_custom_filters(filters):
    """
    Validate and standardize all custom filters.
    """

    if not isinstance(filters, list):
        raise ValueError(
            "Filters must be provided as a list."
        )

    if not filters:
        raise ValueError(
            "At least one filter is required."
        )

    return [
        validate_custom_filter(
            filter_item
        )
        for filter_item in filters
    ]


# ============================================================
# CUSTOM SCREENING
# ============================================================

def run_custom_screener(
    filters,
    rows=None,
    rank_results=True,
    limit=None,
):
    """
    Execute user-defined screener conditions.

    All filters use AND logic.

    Example:
        ROE > 15
        AND D/E < 1
        AND Revenue CAGR 5Y > 10
    """

    validated_filters = (
        validate_custom_filters(
            filters
        )
    )

    if rows is None:
        rows = load_screener_data()

    filtered_rows = apply_filters(
        rows,
        validated_filters,
    )

    if rank_results:
        filtered_rows = rank_companies(
            filtered_rows
        )

    if limit is not None:

        try:
            limit = int(limit)
        except (TypeError, ValueError):
            raise ValueError(
                "Limit must be an integer."
            )

        if limit <= 0:
            raise ValueError(
                "Limit must be greater than zero."
            )

        filtered_rows = (
            filtered_rows[:limit]
        )

    return {
        "filters": validated_filters,
        "total_universe": len(rows),
        "matched_count": len(
            filtered_rows
        ),
        "ranked": rank_results,
        "results": filtered_rows,
    }


# ============================================================
# RESULT EXPLANATION
# ============================================================

def explain_match(
    row,
    filters,
):
    """
    Produce readable reasons explaining why a company
    matched a custom screen.
    """

    explanations = []

    for filter_item in filters:

        metric = filter_item[
            "metric"
        ]

        operator = filter_item[
            "operator"
        ]

        threshold = filter_item[
            "value"
        ]

        actual = row.get(metric)

        explanations.append(
            {
                "metric": metric,
                "actual": actual,
                "operator": operator,
                "threshold": threshold,
            }
        )

    return explanations


# ============================================================
# DAY 18 QA
# ============================================================

def main():

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

    output = run_custom_screener(
        filters
    )

    print(
        "\n=== SPRINT 3 - DAY 18 "
        "CUSTOM SCREENER QA ==="
    )

    print(
        "Universe:",
        output["total_universe"],
    )

    print(
        "Filters:",
        len(output["filters"]),
    )

    print(
        "Matches:",
        output["matched_count"],
    )

    print(
        "Ranked:",
        output["ranked"],
    )

    print(
        "\nFILTERS"
    )

    for filter_item in (
        output["filters"]
    ):

        print(
            filter_item["metric"],
            filter_item["operator"],
            filter_item["value"],
        )

    print(
        "\nTOP 20 MATCHES"
    )

    for row in (
        output["results"][:20]
    ):

        print(
            row.get("rank"),
            "|",
            row["company_id"],
            "|",
            row["company_name"],
            "| Score:",
            row.get(
                "composite_score"
            ),
            "| ROE:",
            row.get("roe_pct"),
            "| D/E:",
            row.get("de_ratio"),
            "| Revenue CAGR:",
            row.get(
                "revenue_cagr_5yr"
            ),
        )


if __name__ == "__main__":
    main()