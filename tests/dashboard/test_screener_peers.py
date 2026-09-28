"""Sprint 4 - Day 24 tests for Screener and Peer Comparison."""

from src.screener.engine import (
    SUPPORTED_FILTERS,
    run_screener,
)

from src.screener.scoring import (
    rank_companies,
)

from src.analytics.peer_comparison import (
    PEER_METRICS,
    load_peer_comparison_data,
)


# ============================================================
# SCREENER TESTS
# ============================================================

def test_screener_has_15_supported_metrics():
    assert len(SUPPORTED_FILTERS) == 15


def test_expected_screener_metrics():
    expected = {
        "asset_turnover",
        "cfo_margin_pct",
        "de_ratio",
        "dividend_yield_pct",
        "eps_cagr_5yr",
        "icr",
        "market_cap_crore",
        "npm_pct",
        "opm_pct",
        "pat_cagr_5yr",
        "pb_ratio",
        "pe_ratio",
        "revenue_cagr_5yr",
        "roce_pct",
        "roe_pct",
    }

    assert SUPPORTED_FILTERS == expected


def test_default_dashboard_screener():
    filters = [
        {
            "metric": "roe_pct",
            "operator": ">=",
            "value": 15.0,
        },
        {
            "metric": "de_ratio",
            "operator": ">=",
            "value": 1.0,
        },
        {
            "metric": "revenue_cagr_5yr",
            "operator": ">=",
            "value": 10.0,
        },
    ]

    results = run_screener(filters)

    assert len(results) == 14


def test_screener_results_have_company_ids():
    results = run_screener(
        [
            {
                "metric": "roe_pct",
                "operator": ">=",
                "value": 15.0,
            }
        ]
    )

    assert results

    assert all(
        row.get("company_id")
        for row in results
    )


def test_screener_results_can_be_scored():
    results = run_screener(
        [
            {
                "metric": "roe_pct",
                "operator": ">=",
                "value": 15.0,
            }
        ]
    )

    ranked = rank_companies(results)

    assert len(ranked) == len(results)


# ============================================================
# PEER TESTS
# ============================================================

def test_peer_metric_count():
    assert len(PEER_METRICS) == 15


def test_peer_data_has_840_rows():
    rows = load_peer_comparison_data()

    assert len(rows) == 840


def test_peer_data_has_11_groups():
    rows = load_peer_comparison_data()

    groups = {
        row[0]
        for row in rows
    }

    assert len(groups) == 11


def test_peer_data_has_56_companies():
    rows = load_peer_comparison_data()

    companies = {
        row[1]
        for row in rows
    }

    assert len(companies) == 56


def test_one_benchmark_per_peer_group():
    rows = load_peer_comparison_data()

    benchmarks = {}

    for row in rows:
        group = row[0]
        company_id = row[1]
        is_benchmark = bool(row[3])

        if is_benchmark:
            benchmarks.setdefault(
                group,
                set(),
            ).add(company_id)

    assert len(benchmarks) == 11

    assert all(
        len(company_ids) == 1
        for company_ids
        in benchmarks.values()
    )


def test_automobiles_group():
    rows = load_peer_comparison_data()

    automobile_rows = [
        row
        for row in rows
        if row[0] == "Automobiles"
    ]

    companies = {
        row[1]
        for row in automobile_rows
    }

    assert len(companies) == 7


def test_automobiles_benchmark_is_maruti():
    rows = load_peer_comparison_data()

    benchmarks = {
        row[1]
        for row in rows
        if (
            row[0] == "Automobiles"
            and bool(row[3])
        )
    }

    assert benchmarks == {"MARUTI"}


def test_peer_percentiles_valid():
    rows = load_peer_comparison_data()

    populated = [
        row[7]
        for row in rows
        if row[7] is not None
    ]

    assert populated

    assert all(
        0 <= value <= 100
        for value in populated
    )