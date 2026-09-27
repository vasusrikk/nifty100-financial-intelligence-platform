"""Sprint 3 - Day 17: Screener Scoring and Ranking Engine."""

from __future__ import annotations

import math
from statistics import median

from src.screener.engine import load_screener_data


# ============================================================
# SCORING CONFIGURATION
# ============================================================

SCORING_WEIGHTS = {
    "roe_pct": 0.20,
    "roce_pct": 0.15,
    "npm_pct": 0.10,
    "revenue_cagr_5yr": 0.15,
    "pat_cagr_5yr": 0.15,
    "de_ratio": 0.10,
    "icr": 0.10,
    "cfo_margin_pct": 0.05,
}

LOWER_IS_BETTER = {
    "de_ratio",
}

HIGHER_IS_BETTER = {
    metric
    for metric in SCORING_WEIGHTS
    if metric not in LOWER_IS_BETTER
}


# ============================================================
# VALUE HELPERS
# ============================================================

def valid_number(value):
    """
    Return True only for usable finite numeric values.
    """

    if value is None:
        return False

    try:
        number = float(value)
    except (TypeError, ValueError):
        return False

    return math.isfinite(number)


def percentile(values, percent):
    """
    Calculate percentile using linear interpolation.
    """

    clean = sorted(
        float(value)
        for value in values
        if valid_number(value)
    )

    if not clean:
        return None

    if len(clean) == 1:
        return clean[0]

    position = (
        (len(clean) - 1)
        * percent
        / 100
    )

    lower = math.floor(position)
    upper = math.ceil(position)

    if lower == upper:
        return clean[lower]

    fraction = position - lower

    return (
        clean[lower]
        + (
            clean[upper]
            - clean[lower]
        ) * fraction
    )


# ============================================================
# WINSORISATION
# ============================================================

def get_winsor_bounds(
    rows,
    metric,
    lower_percentile=5,
    upper_percentile=95,
):
    """
    Obtain lower and upper winsorisation boundaries.

    Raw database values are never modified.
    """

    values = [
        row.get(metric)
        for row in rows
        if valid_number(
            row.get(metric)
        )
    ]

    if not values:
        return None, None

    lower = percentile(
        values,
        lower_percentile,
    )

    upper = percentile(
        values,
        upper_percentile,
    )

    return lower, upper


def winsorize_value(
    value,
    lower,
    upper,
):
    """
    Clamp an extreme value to the configured boundaries.
    """

    if not valid_number(value):
        return None

    value = float(value)

    if lower is not None:
        value = max(
            value,
            lower,
        )

    if upper is not None:
        value = min(
            value,
            upper,
        )

    return value


# ============================================================
# NORMALIZATION
# ============================================================

def normalize_value(
    value,
    minimum,
    maximum,
    higher_is_better=True,
):
    """
    Convert a KPI into a 0-100 normalized score.
    """

    if not valid_number(value):
        return None

    if minimum is None or maximum is None:
        return None

    value = float(value)
    minimum = float(minimum)
    maximum = float(maximum)

    if maximum == minimum:
        return 50.0

    score = (
        (value - minimum)
        / (maximum - minimum)
    ) * 100

    score = max(
        0.0,
        min(score, 100.0),
    )

    if not higher_is_better:
        score = 100.0 - score

    return round(
        score,
        4,
    )


# ============================================================
# METRIC SCORING
# ============================================================

def prepare_metric_bounds(
    rows,
):
    """
    Prepare winsorized min/max values for every scoring KPI.
    """

    bounds = {}

    for metric in SCORING_WEIGHTS:

        lower, upper = get_winsor_bounds(
            rows,
            metric,
        )

        bounds[metric] = {
            "lower": lower,
            "upper": upper,
        }

    return bounds


def score_metric(
    value,
    metric,
    bounds,
):
    """
    Winsorize and normalize one KPI.
    """

    metric_bounds = bounds[
        metric
    ]

    lower = metric_bounds[
        "lower"
    ]

    upper = metric_bounds[
        "upper"
    ]

    adjusted = winsorize_value(
        value,
        lower,
        upper,
    )

    if adjusted is None:
        return None

    return normalize_value(
        adjusted,
        lower,
        upper,
        higher_is_better=(
            metric
            not in LOWER_IS_BETTER
        ),
    )


# ============================================================
# COMPANY COMPOSITE SCORE
# ============================================================

def score_company(
    row,
    bounds,
):
    """
    Calculate a weighted 0-100 score.

    Missing KPIs do not automatically become zero.
    Available weights are re-normalized so that companies
    are scored only on measurable KPIs.
    """

    metric_scores = {}

    weighted_total = 0.0
    available_weight = 0.0

    for metric, weight in (
        SCORING_WEIGHTS.items()
    ):

        score = score_metric(
            row.get(metric),
            metric,
            bounds,
        )

        metric_scores[metric] = score

        if score is None:
            continue

        weighted_total += (
            score * weight
        )

        available_weight += weight

    if available_weight == 0:
        composite_score = None
    else:
        composite_score = (
            weighted_total
            / available_weight
        )

    if composite_score is not None:
        composite_score = round(
            composite_score,
            2,
        )

    result = dict(row)

    result["metric_scores"] = (
        metric_scores
    )

    result["score_coverage_pct"] = (
        round(
            available_weight * 100,
            2,
        )
    )

    result["composite_score"] = (
        composite_score
    )

    return result


# ============================================================
# RANKING
# ============================================================

def rank_companies(
    rows=None,
):
    """
    Score and rank the screener universe.

    Tie-break:
    1. Higher composite score
    2. Higher score coverage
    3. Alphabetical company ID

    This guarantees deterministic ranking.
    """

    if rows is None:
        rows = load_screener_data()

    bounds = prepare_metric_bounds(
        rows
    )

    scored = [
        score_company(
            row,
            bounds,
        )
        for row in rows
    ]

    scored = [
        row
        for row in scored
        if row["composite_score"]
        is not None
    ]

    scored.sort(
        key=lambda row: (
            -row["composite_score"],
            -row["score_coverage_pct"],
            str(
                row["company_id"]
            ),
        )
    )

    for index, row in enumerate(
        scored,
        start=1,
    ):
        row["rank"] = index

    return scored


# ============================================================
# DAY 17 QA
# ============================================================

def main():

    rows = load_screener_data()

    ranked = rank_companies(
        rows
    )

    print(
        "\n=== SPRINT 3 - DAY 17 "
        "SCORING & RANKING QA ==="
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
        "Scoring metrics:",
        len(SCORING_WEIGHTS),
    )

    print(
        "Weight total:",
        round(
            sum(
                SCORING_WEIGHTS.values()
            ),
            2,
        ),
    )

    # --------------------------------------------------------
    # Extreme-value verification
    # --------------------------------------------------------

    roe_values = [
        row["roe_pct"]
        for row in rows
        if valid_number(
            row.get("roe_pct")
        )
    ]

    roe_lower, roe_upper = (
        get_winsor_bounds(
            rows,
            "roe_pct",
        )
    )

    print(
        "\nROE raw maximum:",
        max(roe_values)
        if roe_values
        else None,
    )

    print(
        "ROE winsor upper bound:",
        round(roe_upper, 2)
        if roe_upper is not None
        else None,
    )

    # --------------------------------------------------------
    # Top 20
    # --------------------------------------------------------

    print(
        "\nTOP 20 RANKED COMPANIES"
    )

    for row in ranked[:20]:

        print(
            row["rank"],
            "|",
            row["company_id"],
            "|",
            row["company_name"],
            "| Score:",
            row["composite_score"],
            "| Coverage:",
            row["score_coverage_pct"],
        )


if __name__ == "__main__":
    main()