import pytest

from src.analytics.cashflow_kpis import (
    cfo_margin,
    cfo_to_pat,
    cfo_to_pat_flag,
    free_cash_flow,
    fcf_margin,
    capex_to_sales,
    NORMAL,
    ZERO_PAT,
    NEGATIVE_PAT,
    MISSING,
)


# 1. CFO Margin normal case
def test_cfo_margin_normal():
    assert cfo_margin(200, 1000) == pytest.approx(20.0)


# 2. CFO Margin zero sales
def test_cfo_margin_zero_sales():
    assert cfo_margin(200, 0) is None


# 3. CFO Margin missing CFO
def test_cfo_margin_missing():
    assert cfo_margin(None, 1000) is None


# 4. CFO/PAT normal case
def test_cfo_to_pat_normal():
    assert cfo_to_pat(300, 150) == pytest.approx(2.0)


# 5. CFO/PAT zero PAT
def test_cfo_to_pat_zero_pat():
    assert cfo_to_pat(300, 0) is None
    assert cfo_to_pat_flag(300, 0) == ZERO_PAT


# 6. CFO/PAT negative PAT
def test_cfo_to_pat_negative_pat():
    assert cfo_to_pat(300, -100) == pytest.approx(-3.0)
    assert cfo_to_pat_flag(300, -100) == NEGATIVE_PAT


# 7. CFO/PAT missing value
def test_cfo_to_pat_missing():
    assert cfo_to_pat(None, 100) is None
    assert cfo_to_pat_flag(None, 100) == MISSING


# 8. CFO/PAT normal flag
def test_cfo_to_pat_normal_flag():
    assert cfo_to_pat_flag(300, 100) == NORMAL


# 9. FCF normal case
def test_free_cash_flow():
    assert free_cash_flow(500, 200) == pytest.approx(300.0)


# 10. FCF unavailable without Capex
def test_fcf_missing_capex():
    assert free_cash_flow(500, None) is None


# 11. FCF Margin normal
def test_fcf_margin():
    assert fcf_margin(250, 1000) == pytest.approx(25.0)


# 12. FCF Margin zero sales
def test_fcf_margin_zero_sales():
    assert fcf_margin(250, 0) is None


# 13. Capex/Sales normal
def test_capex_to_sales():
    assert capex_to_sales(100, 1000) == pytest.approx(10.0)


# 14. Capex/Sales unavailable without Capex
def test_capex_to_sales_missing_capex():
    assert capex_to_sales(None, 1000) is None