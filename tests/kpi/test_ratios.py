import pytest


from src.analytics.ratios import (
    net_profit_margin,
    operating_profit_margin,
    validate_opm,
    return_on_equity,
    return_on_capital_employed,
    return_on_assets,
    is_financial_sector,
    debt_to_equity,
    leverage_flag,
    interest_coverage_ratio,
    interest_coverage_flag,
    net_debt,
    asset_turnover,
    roce_benchmark_flag,
)

# 1. NPM normal case
def test_npm_normal():
    assert net_profit_margin(20, 100) == pytest.approx(20.0)


# 2. NPM zero sales
def test_npm_zero_sales():
    assert net_profit_margin(20, 0) is None


# 3. OPM normal case
def test_opm_normal():
    assert operating_profit_margin(25, 100) == pytest.approx(25.0)


# 4. OPM zero sales
def test_opm_zero_sales():
    assert operating_profit_margin(25, 0) is None


# 5. OPM cross-check passes
def test_opm_validation_pass():
    assert validate_opm(20.0, 20.5) == "PASS"


# 6. OPM cross-check mismatch > 1 percentage point
def test_opm_validation_mismatch():
    assert validate_opm(20.0, 22.0) == "MISMATCH"


# 7. OPM missing value
def test_opm_validation_missing():
    assert validate_opm(None, 20.0) == "MISSING"


# 8. ROE normal case
def test_roe_normal():
    result = return_on_equity(
        net_profit=20,
        equity_capital=40,
        reserves=60,
    )
    assert result == pytest.approx(20.0)


# 9. ROE non-positive equity
def test_roe_non_positive_equity():
    assert return_on_equity(20, 40, -40) is None


# 10. ROCE normal case
def test_roce_normal():
    result = return_on_capital_employed(
        ebit=30,
        equity_capital=40,
        reserves=60,
        borrowings=50,
    )
    assert result == pytest.approx(20.0)


# 11. ROCE zero capital employed
def test_roce_zero_capital():
    assert return_on_capital_employed(30, 0, 0, 0) is None


# 12. ROA normal case
def test_roa_normal():
    assert return_on_assets(25, 200) == pytest.approx(12.5)


# 13. ROA zero assets
def test_roa_zero_assets():
    assert return_on_assets(25, 0) is None


# 14. Financial-sector detection
def test_financial_sector():
    assert is_financial_sector("Financials") is True


# 15. Non-financial-sector detection
def test_non_financial_sector():
    assert is_financial_sector("Technology") is False























# =========================================================
# DAY 09 - LEVERAGE & EFFICIENCY TESTS
# =========================================================


# 16. D/E normal case
def test_debt_to_equity_normal():
    result = debt_to_equity(
        borrowings=100,
        equity_capital=40,
        reserves=60,
    )
    assert result == pytest.approx(1.0)


# 17. Debt-free D/E
def test_debt_to_equity_debt_free():
    assert debt_to_equity(0, 40, 60) == 0.0


# 18. D/E with non-positive equity
def test_debt_to_equity_invalid_equity():
    assert debt_to_equity(100, 40, -40) is None


# 19. High leverage flag
def test_high_leverage_flag():
    assert (
        leverage_flag(5.5, "Technology")
        == "HIGH_LEVERAGE"
    )


# 20. Financial-sector D/E carve-out
def test_financial_leverage_flag():
    assert (
        leverage_flag(3.0, "Financials")
        == "SECTOR_RELATIVE"
    )


# 21. ICR normal case
def test_interest_coverage_normal():
    assert interest_coverage_ratio(
        300,
        100,
    ) == pytest.approx(3.0)


# 22. Zero-interest ICR
def test_interest_coverage_zero_interest():
    assert interest_coverage_ratio(
        300,
        0,
    ) is None


# 23. ICR warning
def test_icr_warning():
    assert (
        interest_coverage_flag(
            1.2,
            100,
            20,
        )
        == "ICR_WARNING"
    )


# 24. Debt-free classification
def test_debt_free_flag():
    assert (
        interest_coverage_flag(
            None,
            0,
            0,
        )
        == "DEBT_FREE"
    )


# 25. Net Debt
def test_net_debt():
    assert net_debt(
        500,
        150,
    ) == pytest.approx(350.0)


# 26. Asset Turnover
def test_asset_turnover():
    assert asset_turnover(
        500,
        1000,
    ) == pytest.approx(0.5)


# 27. Asset Turnover zero assets
def test_asset_turnover_zero_assets():
    assert asset_turnover(
        500,
        0,
    ) is None








# =========================================================
# DAY 08 - FINANCIAL-SECTOR ROCE BENCHMARK
# =========================================================

def test_financial_roce_above_sector_median():
    assert (
        roce_benchmark_flag(
            14.0,
            "Financials",
            12.0,
        )
        == "ABOVE_SECTOR_MEDIAN"
    )


def test_financial_roce_below_sector_median():
    assert (
        roce_benchmark_flag(
            9.0,
            "Financials",
            12.0,
        )
        == "BELOW_SECTOR_MEDIAN"
    )


def test_financial_roce_benchmark_unavailable():
    assert (
        roce_benchmark_flag(
            12.0,
            "Financials",
            None,
        )
        == "SECTOR_BENCHMARK_UNAVAILABLE"
    )


def test_non_financial_roce_benchmark_not_applicable():
    assert (
        roce_benchmark_flag(
            18.0,
            "Technology",
            12.0,
        )
        == "NOT_APPLICABLE"
    )







# =========================================================
# DAY 08 - FINANCIAL-SECTOR ROCE BENCHMARK
# =========================================================

def test_financial_roce_above_sector_median():
    assert roce_benchmark_flag(
        14.0, "Financials", 12.0
    ) == "ABOVE_SECTOR_MEDIAN"


def test_financial_roce_below_sector_median():
    assert roce_benchmark_flag(
        9.0, "Financials", 12.0
    ) == "BELOW_SECTOR_MEDIAN"


def test_financial_roce_benchmark_unavailable():
    assert roce_benchmark_flag(
        12.0, "Financials", None
    ) == "SECTOR_BENCHMARK_UNAVAILABLE"


def test_non_financial_roce_benchmark_not_applicable():
    assert roce_benchmark_flag(
        18.0, "Technology", 12.0
    ) == "NOT_APPLICABLE"