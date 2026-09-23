import pytest

from src.analytics.cagr import (
    calculate_cagr,
    calculate_window_cagr,
    NORMAL,
    DECLINE_TO_LOSS,
    TURNAROUND,
    BOTH_NEGATIVE,
    ZERO_BASE,
    INSUFFICIENT,
)


# 1. Normal positive-to-positive CAGR
def test_normal_cagr():
    value, flag = calculate_cagr(100, 121, 2)

    assert value == pytest.approx(10.0)
    assert flag == NORMAL


# 2. Positive start -> negative end
def test_decline_to_loss():
    value, flag = calculate_cagr(100, -20, 5)

    assert value is None
    assert flag == DECLINE_TO_LOSS


# 3. Negative start -> positive end
def test_turnaround():
    value, flag = calculate_cagr(-100, 50, 5)

    assert value is None
    assert flag == TURNAROUND


# 4. Negative start -> negative end
def test_both_negative():
    value, flag = calculate_cagr(-100, -50, 5)

    assert value is None
    assert flag == BOTH_NEGATIVE


# 5. Zero base
def test_zero_base():
    value, flag = calculate_cagr(0, 100, 5)

    assert value is None
    assert flag == ZERO_BASE


# 6. Missing start value
def test_missing_start_value():
    value, flag = calculate_cagr(None, 100, 5)

    assert value is None
    assert flag == INSUFFICIENT


# 7. Missing end value
def test_missing_end_value():
    value, flag = calculate_cagr(100, None, 5)

    assert value is None
    assert flag == INSUFFICIENT


# 8. Insufficient historical data
def test_insufficient_history():
    value, flag = calculate_window_cagr(
        start_value=100,
        end_value=150,
        available_years=3,
        required_years=5,
    )

    assert value is None
    assert flag == INSUFFICIENT


# 9. Valid 5-year window
def test_valid_five_year_window():
    value, flag = calculate_window_cagr(
        start_value=100,
        end_value=161.051,
        available_years=5,
        required_years=5,
    )

    assert value == pytest.approx(10.0, abs=0.01)
    assert flag == NORMAL


# 10. Positive value declining to zero
def test_positive_to_zero():
    value, flag = calculate_cagr(100, 0, 5)

    assert value == pytest.approx(-100.0)
    assert flag == NORMAL