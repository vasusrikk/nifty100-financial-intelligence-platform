"""Sprint 4 - Day 26 tests for the Valuation Module."""

import pandas as pd

from src.analytics.valuation import (
    VALUATION_YEAR,
    add_fcf_yield,
    build_valuation_summary,
    classify_metric,
)


def test_valuation_universe():
    data = build_valuation_summary()

    assert len(data) == 92
    assert data["company_id"].nunique() == 92


def test_valuation_year():
    data = build_valuation_summary()

    assert set(data["year"].dropna()) == {
        VALUATION_YEAR
    }


def test_pe_complete():
    data = build_valuation_summary()

    assert data["pe_ratio"].notna().sum() == 92


def test_pb_complete():
    data = build_valuation_summary()

    assert data["pb_ratio"].notna().sum() == 92


def test_ev_ebitda_complete():
    data = build_valuation_summary()

    assert data["ev_ebitda"].notna().sum() == 92


def test_sector_medians_present():
    data = build_valuation_summary()

    required = {
        "sector_median_pe_ratio",
        "sector_median_pb_ratio",
        "sector_median_ev_ebitda",
    }

    assert required.issubset(data.columns)

    for column in required:
        assert data[column].notna().sum() == 92


def test_valuation_flags_present():
    data = build_valuation_summary()

    required = {
        "pe_ratio_flag",
        "pb_ratio_flag",
        "ev_ebitda_flag",
    }

    assert required.issubset(data.columns)

def test_caution_classification():
    assert (
        classify_metric(160, 100)
        == "Caution"
    )


def test_discount_classification():
    assert (
        classify_metric(60, 100)
        == "Discount"
    )


def test_in_line_classification():
    assert (
        classify_metric(100, 100)
        == "In Line"
    )

def test_unavailable_classification():
    assert (
        classify_metric(None, 100)
        == "Unavailable"
    )


def test_fcf_yield_not_fabricated():
    data = build_valuation_summary()

    assert data["fcf"].notna().sum() == 0
    assert data["fcf_yield_pct"].notna().sum() == 0


def test_fcf_yield_status():
    data = build_valuation_summary()

    assert (
        data["fcf_yield_status"]
        == "Unavailable - source FCF absent"
    ).all()


def test_fcf_yield_formula_when_source_exists():
    sample = pd.DataFrame(
        [
            {
                "fcf": 50.0,
                "market_cap_crore": 1000.0,
            }
        ]
    )

    result = add_fcf_yield(sample)

    assert result.iloc[0]["fcf_yield_pct"] == 5.0
    assert (
        result.iloc[0]["fcf_yield_status"]
        == "Available"
    )