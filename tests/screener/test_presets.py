import pytest

from src.screener.engine import load_screener_data
from src.screener.presets import (
    PRESETS,
    get_revenue_cagr_3yr,
    is_de_declining,
    run_preset,
)


# ============================================================
# PRESET DEFINITIONS
# ============================================================

def test_six_presets_exist():
    assert len(PRESETS) == 6


def test_expected_preset_names():
    expected = {
        "quality_compounder",
        "value_pick",
        "growth_accelerator",
        "dividend_champion",
        "debt_free_blue_chip",
        "turnaround_watch",
    }

    assert set(PRESETS.keys()) == expected


def test_quality_compounder_definition():
    preset = PRESETS["quality_compounder"]

    assert preset["requires_fcf"] is True
    assert len(preset["filters"]) == 3


def test_value_pick_definition():
    preset = PRESETS["value_pick"]

    filters = preset["filters"]

    assert {
        "metric": "pe_ratio",
        "operator": "<",
        "value": 20,
    } in filters

    assert {
        "metric": "pb_ratio",
        "operator": "<",
        "value": 3.0,
    } in filters

    assert {
        "metric": "de_ratio",
        "operator": "<",
        "value": 2.0,
    } in filters

    assert {
        "metric": "dividend_yield_pct",
        "operator": ">",
        "value": 1,
    } in filters


def test_growth_accelerator_definition():
    preset = PRESETS["growth_accelerator"]

    assert {
        "metric": "pat_cagr_5yr",
        "operator": ">",
        "value": 20,
    } in preset["filters"]

    assert {
        "metric": "revenue_cagr_5yr",
        "operator": ">",
        "value": 15,
    } in preset["filters"]


def test_dividend_champion_definition():
    preset = PRESETS["dividend_champion"]

    assert preset[
        "requires_dividend_payout"
    ] is True

    assert preset["requires_fcf"] is True


def test_debt_free_blue_chip_definition():
    preset = PRESETS["debt_free_blue_chip"]

    assert preset[
        "requires_revenue"
    ] is True

    assert {
        "metric": "de_ratio",
        "operator": "==",
        "value": 0,
    } in preset["filters"]

    assert {
        "metric": "roe_pct",
        "operator": ">",
        "value": 12,
    } in preset["filters"]


def test_turnaround_watch_definition():
    preset = PRESETS["turnaround_watch"]

    assert preset[
        "requires_revenue_cagr_3yr"
    ] is True

    assert preset[
        "requires_de_declining"
    ] is True

    assert preset[
        "requires_fcf"
    ] is True


# ============================================================
# HISTORICAL CALCULATIONS
# ============================================================

def test_abb_revenue_cagr_3yr():
    value = get_revenue_cagr_3yr(
        "ABB"
    )

    assert value is not None
    assert value > 10


def test_adaniports_revenue_cagr_3yr():
    value = get_revenue_cagr_3yr(
        "ADANIPORTS"
    )

    assert value is not None
    assert value > 20


def test_abb_de_declining():
    assert is_de_declining(
        "ABB"
    ) is True


def test_adaniports_de_declining():
    assert is_de_declining(
        "ADANIPORTS"
    ) is True


def test_unknown_company_cagr():
    assert get_revenue_cagr_3yr(
        "NOT_A_REAL_COMPANY"
    ) is None


def test_unknown_company_de_trend():
    assert is_de_declining(
        "NOT_A_REAL_COMPANY"
    ) is False


# ============================================================
# PRESET EXECUTION
# ============================================================

def test_value_pick_runs():
    result = run_preset(
        "value_pick"
    )

    assert result["status"] == "COMPLETE"
    assert len(result["results"]) == 2


def test_growth_accelerator_runs():
    result = run_preset(
        "growth_accelerator"
    )

    assert result["status"] == "COMPLETE"
    assert len(result["results"]) > 0


def test_debt_free_blue_chip_runs():
    result = run_preset(
        "debt_free_blue_chip"
    )

    assert result["status"] == "COMPLETE"

    for row in result["results"]:
        assert row["de_ratio"] == 0
        assert row["roe_pct"] > 12
        assert row["sales"] > 5000


# ============================================================
# FCF SOURCE LIMITATION
# ============================================================

@pytest.mark.parametrize(
    "preset_key",
    [
        "quality_compounder",
        "dividend_champion",
        "turnaround_watch",
    ],
)
def test_fcf_presets_report_source_limitation(
    preset_key,
):
    result = run_preset(
        preset_key
    )

    assert (
        result["status"]
        == "SOURCE_LIMITATION"
    )

    assert "FCF" in result["reason"]

    assert "partial_results" in result


def test_turnaround_partial_conditions():
    result = run_preset(
        "turnaround_watch"
    )

    for row in result["partial_results"]:

        assert (
            row["revenue_cagr_3yr"]
            > 10
        )

        assert is_de_declining(
            row["company_id"]
        )


def test_dividend_partial_payout():
    result = run_preset(
        "dividend_champion"
    )

    for row in result["partial_results"]:

        assert (
            row["dividend_yield_pct"]
            > 2
        )

        assert (
            row["dividend_payout"]
            < 80
        )


# ============================================================
# ERROR HANDLING
# ============================================================

def test_invalid_preset():
    with pytest.raises(ValueError):
        run_preset(
            "not_a_real_preset"
        )


# ============================================================
# UNIVERSE INTEGRITY
# ============================================================

def test_preset_universe_unique():
    rows = load_screener_data()

    company_ids = [
        row["company_id"]
        for row in rows
    ]

    assert len(company_ids) == len(
        set(company_ids)
    )