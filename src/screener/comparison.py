"""Sprint 3 - Day 19: Company Comparison Engine."""

from __future__ import annotations

from src.screener.engine import load_screener_data
from src.screener.scoring import (
    prepare_metric_bounds,
    score_company,
)


# ============================================================
# COMPARISON CONFIGURATION
# ============================================================

COMPARISON_METRICS = [
    "roe_pct",
    "roce_pct",
    "npm_pct",
    "opm_pct",
    "de_ratio",
    "icr",
    "asset_turnover",
    "revenue_cagr_5yr",
    "pat_cagr_5yr",
    "eps_cagr_5yr",
    "cfo_margin_pct",
    "pe_ratio",
    "pb_ratio",
    "dividend_yield_pct",
    "market_cap_crore",
]


METRIC_LABELS = {
    "roe_pct": "ROE (%)",
    "roce_pct": "ROCE (%)",
    "npm_pct": "Net Profit Margin (%)",
    "opm_pct": "Operating Profit Margin (%)",
    "de_ratio": "Debt / Equity",
    "icr": "Interest Coverage Ratio",
    "asset_turnover": "Asset Turnover",
    "revenue_cagr_5yr": "Revenue CAGR 5Y (%)",
    "pat_cagr_5yr": "PAT CAGR 5Y (%)",
    "eps_cagr_5yr": "EPS CAGR 5Y (%)",
    "cfo_margin_pct": "CFO Margin (%)",
    "pe_ratio": "P/E",
    "pb_ratio": "P/B",
    "dividend_yield_pct": "Dividend Yield (%)",
    "market_cap_crore": "Market Cap (₹ Cr)",
}


# ============================================================
# COMPANY LOOKUP
# ============================================================

def build_company_index(rows):
    """
    Build company_id -> company row mapping.
    """

    return {
        str(row["company_id"]).upper(): row
        for row in rows
    }


def get_company(
    company_id,
    rows=None,
):
    """
    Retrieve one company from the screener universe.
    """

    if rows is None:
        rows = load_screener_data()

    company_id = str(
        company_id
    ).strip().upper()

    index = build_company_index(
        rows
    )

    if company_id not in index:
        raise ValueError(
            f"Company not found: {company_id}"
        )

    return index[company_id]


# ============================================================
# METRIC COMPARISON
# ============================================================

def compare_metric_values(
    companies,
    metric,
):
    """
    Return raw values for one metric across companies.

    No winner is declared here because sector context and
    metric interpretation can differ.
    """

    if metric not in COMPARISON_METRICS:
        raise ValueError(
            f"Unsupported comparison metric: {metric}"
        )

    return [
        {
            "company_id": row["company_id"],
            "value": row.get(metric),
        }
        for row in companies
    ]


# ============================================================
# COMPANY COMPARISON
# ============================================================

def compare_companies(
    company_ids,
    rows=None,
):
    """
    Compare 2-5 companies side by side.

    Returns:
    - company identity
    - financial period
    - sector
    - raw comparison metrics
    - Day 17 composite score
    - score coverage
    """

    if not isinstance(
        company_ids,
        (list, tuple),
    ):
        raise ValueError(
            "Company IDs must be provided as a list."
        )

    cleaned_ids = [
        str(company_id).strip().upper()
        for company_id in company_ids
        if str(company_id).strip()
    ]

    if len(cleaned_ids) < 2:
        raise ValueError(
            "Select at least two companies for comparison."
        )

    if len(cleaned_ids) > 5:
        raise ValueError(
            "A maximum of five companies can be compared."
        )

    if len(cleaned_ids) != len(
        set(cleaned_ids)
    ):
        raise ValueError(
            "Duplicate companies are not allowed."
        )

    if rows is None:
        rows = load_screener_data()

    selected = [
        get_company(
            company_id,
            rows,
        )
        for company_id in cleaned_ids
    ]

    # Use the full screener universe to establish scoring
    # boundaries. This keeps comparison scores consistent with
    # Day 17 universe-level scoring.
    bounds = prepare_metric_bounds(
        rows
    )

    scored_companies = [
        score_company(
            company,
            bounds,
        )
        for company in selected
    ]

    companies = []

    for row in scored_companies:

        metrics = {
            metric: row.get(metric)
            for metric in COMPARISON_METRICS
        }

        companies.append(
            {
                "company_id": row[
                    "company_id"
                ],
                "company_name": row[
                    "company_name"
                ],
                "year": row.get(
                    "year"
                ),
                "broad_sector": row.get(
                    "broad_sector"
                ),
                "sub_sector": row.get(
                    "sub_sector"
                ),
                "metrics": metrics,
                "composite_score": row.get(
                    "composite_score"
                ),
                "score_coverage_pct": row.get(
                    "score_coverage_pct"
                ),
            }
        )

    metric_comparison = {}

    for metric in COMPARISON_METRICS:

        metric_comparison[metric] = {
            "label": METRIC_LABELS[
                metric
            ],
            "values": compare_metric_values(
                scored_companies,
                metric,
            ),
        }

    return {
        "company_count": len(
            companies
        ),
        "companies": companies,
        "metrics": metric_comparison,
    }


# ============================================================
# DAY 19 QA
# ============================================================

def main():

    selected = [
        "TCS",
        "INFY",
        "HCLTECH",
    ]

    output = compare_companies(
        selected
    )

    print(
        "\n=== SPRINT 3 - DAY 19 "
        "COMPANY COMPARISON QA ==="
    )

    print(
        "Companies:",
        output["company_count"],
    )

    print(
        "Metrics:",
        len(
            output["metrics"]
        ),
    )

    print(
        "\nCOMPANY SUMMARY"
    )

    for company in output[
        "companies"
    ]:

        print(
            company["company_id"],
            "|",
            company["company_name"],
            "| FY:",
            company["year"],
            "| Sector:",
            company["broad_sector"],
            "| Score:",
            company["composite_score"],
            "| Coverage:",
            company["score_coverage_pct"],
        )

    print(
        "\nSIDE-BY-SIDE METRICS"
    )

    for metric, data in (
        output["metrics"].items()
    ):

        values = " | ".join(
            (
                f"{item['company_id']}: "
                f"{item['value']}"
            )
            for item in data["values"]
        )

        print(
            data["label"],
            "|",
            values,
        )


if __name__ == "__main__":
    main()