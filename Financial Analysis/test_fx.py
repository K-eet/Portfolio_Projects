"""
test_fx.py
Unit tests for fx.py — the flow/stock rate distinction is the part that has to
be right, so it is what these tests pin down.
"""

import pandas as pd
import pytest

from fx import to_usd

RATES = pd.DataFrame(
    {"average": [7.0, 7.2], "year_end": [7.5, 7.4]}, index=[2023, 2024]
).rename_axis("Year")


def test_flow_uses_average_rate():
    # A full-year flow translates at the year's average rate.
    assert to_usd(70.0, 2023, RATES, "flow") == 10.0


def test_stock_uses_year_end_rate():
    # A balance-sheet snapshot translates at the year-end rate.
    assert to_usd(75.0, 2023, RATES, "stock") == 10.0


def test_flow_and_stock_differ_for_same_input():
    # The whole point of the distinction: same figure, different result.
    assert to_usd(100.0, 2024, RATES, "flow") != to_usd(100.0, 2024, RATES, "stock")


def test_year_is_respected():
    assert to_usd(72.0, 2024, RATES, "flow") == 10.0


def test_unknown_kind_raises():
    # No silent default — choosing wrongly is the bug this module prevents.
    with pytest.raises(ValueError):
        to_usd(100.0, 2023, RATES, "average")


def test_missing_year_raises():
    with pytest.raises(KeyError):
        to_usd(100.0, 2021, RATES, "flow")


def test_byd_2024_regression():
    # Regression guard for the original defect: BYD's 2024 free cash flow was
    # CNY 36.09B, reported in the README as "$36B". At the 2024 average rate it
    # is roughly $5B — not larger than Ford's $6.7B.
    rates = pd.DataFrame({"average": [7.1862], "year_end": [7.2981]}, index=[2024])
    fcf_usd = to_usd(36.094e9, 2024, rates, "flow")
    assert 4.9e9 < fcf_usd < 5.1e9
