"""
test_metrics.py
Unit tests for metrics.py — verifies calculations are correct
and edge cases are handled properly.
"""

import pytest
from metrics import (
    net_profit_margin,
    return_on_assets,
    cash_conversion_ratio,
    price_to_earnings,
    fcf_yield,
    ev_to_ebitda
)


def test_net_profit_margin():
    # Net income of 15, revenue of 100 -> 15% margin
    assert net_profit_margin(15, 100) == 15.0
    
def test_net_profit_margin_negative():
    # Loss-making company should return negative margin
    assert net_profit_margin(-10, 100) == -10.0


def test_return_on_assets():
    assert return_on_assets(10, 200) == 5.0


def test_cash_conversion_ratio():
    # OCF of 20, NI of 10 -> ratio of 2.0
    assert cash_conversion_ratio(20, 10) == 2.0

def test_cash_conversion_ratio_below_one():
    # OCF of 5, NI of 10 -> ratio of 0.5 (red flag case)
    assert cash_conversion_ratio(5, 10) == 0.5


def test_price_to_earnings():
    assert price_to_earnings(1000, 100) == 10.0

def test_price_to_earnings_negative_income():
    # Should return None, not a negative or invalid number
    assert price_to_earnings(1000, -50) is None


def test_fcf_yield():
    assert fcf_yield(50, 1000) == 5.0


def test_ev_to_ebitda():
    # Market cap 1000, debt 200, cash 100, EBITDA 100
    # EV = 1000 + 200 - 100 = 1100, EV/EBITDA = 11.0
    assert ev_to_ebitda(1000, 200, 100, 100) == 11.0

def test_ev_to_ebitda_negative_ebitda():
    assert ev_to_ebitda(1000, 200, 100, -50) is None