"""Sprint 3 - Original Day 17: Sector-Relative Composite Ranking.

Composite Score:
    50% Profitability
    30% Growth
    20% Valuation

Scores are normalized relative to each company's broad sector.
"""

from __future__ import annotations

import math
from collections import defaultdict

from src.screener.engine import load_screener_data


# ============================================================
# DAY 17 SCORING CONFIGURATION
# ============================================================

CATEGORY_WEIGHTS = {
    "profitability": 0.50,
    "growth": 0.30,
    "valuation": 0.20,
}


CATEGORY_METRICS = {
    "profitability": [
        "roe_pct",
        "roce_pct",
        "npm_pct",
        "opm_pct",
        "cfo_margin_pct",
    ],

    "growth": [
        "revenue_cagr_5yr",
        "pat_cagr_5yr",
        "eps_cagr_5yr",
    ],

    "valuation": [
        "pe_ratio",
        "pb_ratio",
    ],
}


# Lower values are preferable for valuation multiples.
LOWER_IS_BETTER = {
    "pe_ratio",
    "pb_ratio",
}


# ============================================================
# VALUE HELPERS
# ============================================================

def valid_number(value):
    """Return True for a usable finite numeric value."""

    if value is None:
        return False

    try:
        number = float(value)
    except (TypeError, ValueError):
        return False

    return math.isfinite(number)


def normalize_value(
    value,
    minimum,
    maximum,
    lower_is_better=False,
):
    """
    Normalize a value to a 0-100 score.

    Normalization is performed only against values from the
    company's own broad sector.
    """

    if not valid_number(value):
        return None

    if (
        minimum is None
        or maximum is None
    ):
        return None

    value = float(value)
    minimum = float(minimum)
    maximum = float(maximum)

    if maximum == minimum:
        return 50.0

    score = (
        (value - minimum)
        / (maximum - minimum)
    ) * 100.0

    score = max(
        0.0,
        min(score, 100.0),
    )

    if lower_is_better:
        score = 100.0 - score

    return round(score, 4)


# ============================================================
# SECTOR GROUPING
# ============================================================

def group_by_sector(rows):
    """
    Group screener rows by broad_sector.
    """

    groups = defaultdict(list)

    for row in rows:

        sector = (
            row.get("broad_sector")
            or "Unknown"
        )

        groups[sector].append(row)

    return dict(groups)


def build_sector_bounds(rows):
    """
    Calculate min/max bounds for every Day 17 metric
    independently inside each broad sector.
    """

    sector_groups = group_by_sector(
        rows
    )

    bounds = {}

    all_metrics = {
        metric
        for metrics in CATEGORY_METRICS.values()
        for metric in metrics
    }

    for sector, companies in (
        sector_groups.items()
    ):

        bounds[sector] = {}

        for metric in all_metrics:

            values = [
                float(row[metric])
                for row in companies
                if valid_number(
                    row.get(metric)
                )
            ]

            if not values:
                minimum = None
                maximum = None
            else:
                minimum = min(values)
                maximum = max(values)

            bounds[sector][metric] = {
                "min": minimum,
                "max": maximum,
            }

    return bounds





















# ============================================================
# INDIVIDUAL METRIC SCORE
# ============================================================

def score_metric(
    row,
    metric,
    sector_bounds,
):
    """
    Calculate the 0-100 sector-relative score
    for one financial metric.
    """

    sector = (
        row.get("broad_sector")
        or "Unknown"
    )

    value = row.get(metric)

    if not valid_number(value):
        return None

    metric_bounds = (
        sector_bounds
        .get(sector, {})
        .get(metric)
    )

    if not metric_bounds:
        return None

    return normalize_value(
        value,
        metric_bounds["min"],
        metric_bounds["max"],
        lower_is_better=(
            metric in LOWER_IS_BETTER
        ),
    )


# ============================================================
# CATEGORY SCORE
# ============================================================

def calculate_category_score(
    row,
    category,
    sector_bounds,
):
    """
    Calculate one category score.

    Available metrics inside the category are averaged.
    Missing metrics are excluded rather than treated as zero.
    """

    metrics = CATEGORY_METRICS[
        category
    ]

    metric_scores = {}

    available_scores = []

    for metric in metrics:

        score = score_metric(
            row,
            metric,
            sector_bounds,
        )

        metric_scores[metric] = score

        if score is not None:
            available_scores.append(
                score
            )

    if not available_scores:
        category_score = None
    else:
        category_score = (
            sum(available_scores)
            / len(available_scores)
        )

        category_score = round(
            category_score,
            4,
        )

    return (
        category_score,
        metric_scores,
    )


# ============================================================
# COMPOSITE SCORE
# ============================================================

def score_company(
    row,
    sector_bounds,
):
    """
    Calculate the original Sprint 3 composite score:

        Profitability  50%
        Growth         30%
        Valuation      20%

    Missing entire categories cause the available category
    weights to be re-normalized rather than being scored zero.
    """

    category_scores = {}
    metric_scores = {}

    weighted_total = 0.0
    available_weight = 0.0

    for category, weight in (
        CATEGORY_WEIGHTS.items()
    ):

        (
            category_score,
            category_metric_scores,
        ) = calculate_category_score(
            row,
            category,
            sector_bounds,
        )

        category_scores[
            category
        ] = category_score

        metric_scores.update(
            category_metric_scores
        )

        if category_score is None:
            continue

        weighted_total += (
            category_score
            * weight
        )

        available_weight += weight

    if available_weight == 0:
        composite_score = None
    else:
        composite_score = (
            weighted_total
            / available_weight
        )

        composite_score = round(
            composite_score,
            2,
        )

    result = dict(row)

    result[
        "profitability_score"
    ] = category_scores.get(
        "profitability"
    )

    result[
        "growth_score"
    ] = category_scores.get(
        "growth"
    )

    result[
        "valuation_score"
    ] = category_scores.get(
        "valuation"
    )

    result[
        "category_scores"
    ] = category_scores

    result[
        "sector_metric_scores"
    ] = metric_scores

    result[
        "composite_score_50_30_20"
    ] = composite_score

    result[
        "score_coverage_pct"
    ] = round(
        available_weight * 100,
        2,
    )

    return result


# ============================================================
# SECTOR-RELATIVE RANKING
# ============================================================

def rank_sector_relative(
    rows=None,
):
    """
    Score the complete universe and rank companies by the
    50/30/20 composite score.

    Ranking is deterministic.
    """

    if rows is None:
        rows = load_screener_data()

    sector_bounds = (
        build_sector_bounds(rows)
    )

    scored = [
        score_company(
            row,
            sector_bounds,
        )
        for row in rows
    ]

    scored = [
        row
        for row in scored
        if row[
            "composite_score_50_30_20"
        ] is not None
    ]

    scored.sort(
        key=lambda row: (
            -row[
                "composite_score_50_30_20"
            ],
            -row[
                "score_coverage_pct"
            ],
            str(
                row["company_id"]
            ),
        )
    )

    for rank, row in enumerate(
        scored,
        start=1,
    ):
        row["overall_rank"] = rank

    # --------------------------------------------------------
    # Rank companies inside their own broad sector
    # --------------------------------------------------------

    sector_groups = defaultdict(
        list
    )

    for row in scored:
        sector_groups[
            row.get("broad_sector")
            or "Unknown"
        ].append(row)

    for companies in (
        sector_groups.values()
    ):

        companies.sort(
            key=lambda row: (
                -row[
                    "composite_score_50_30_20"
                ],
                str(
                    row["company_id"]
                ),
            )
        )

        for rank, row in enumerate(
            companies,
            start=1,
        ):
            row[
                "sector_rank"
            ] = rank

    # Restore overall ordering after assigning sector ranks.
    scored.sort(
        key=lambda row: row[
            "overall_rank"
        ]
    )

    return scored


# ============================================================
# DAY 17 QA
# ============================================================

def main():

    rows = load_screener_data()

    ranked = rank_sector_relative(
        rows
    )

    sectors = group_by_sector(
        rows
    )

    print(
        "\n=== ORIGINAL SPRINT 3 - "
        "DAY 17 SECTOR RANKING QA ==="
    )

    print(
        "Universe:",
        len(rows),
    )

    print(
        "Ranked companies:",
        len(ranked),
    )

    print(
        "Broad sectors:",
        len(sectors),
    )

    print(
        "Category weights:"
    )

    for category, weight in (
        CATEGORY_WEIGHTS.items()
    ):
        print(
            category,
            ":",
            int(weight * 100),
            "%",
        )

    print(
        "\nTOP 20 - 50/30/20 COMPOSITE"
    )

    for row in ranked[:20]:

        print(
            row["overall_rank"],
            "|",
            row["company_id"],
            "|",
            row["broad_sector"],
            "| Profitability:",
            round(
                row["profitability_score"],
                2,
            )
            if row[
                "profitability_score"
            ] is not None
            else None,
            "| Growth:",
            round(
                row["growth_score"],
                2,
            )
            if row[
                "growth_score"
            ] is not None
            else None,
            "| Valuation:",
            round(
                row["valuation_score"],
                2,
            )
            if row[
                "valuation_score"
            ] is not None
            else None,
            "| Composite:",
            row[
                "composite_score_50_30_20"
            ],
            "| Sector Rank:",
            row["sector_rank"],
        )


if __name__ == "__main__":
    main()