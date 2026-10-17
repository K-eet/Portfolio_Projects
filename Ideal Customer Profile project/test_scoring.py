"""
test_scoring.py
Unit tests for scoring.py — each test states the commercial case it encodes,
so that changing a rule means arguing with a sentence, not just a number.
"""

from datetime import date

import pytest

import config
from scoring import (
    parse_sic_code,
    industry_fit,
    company_age_years,
    lifecycle_fit,
    filing_health,
    commercial_substance,
    total_score,
)

AS_OF = date(2026, 9, 1)


# --- SIC parsing -----------------------------------------------------------

def test_parse_sic_code_standard_format():
    assert parse_sic_code("41100 - Development of building projects") == "41100"

def test_parse_sic_code_four_digit():
    # A handful of register entries carry 4-digit codes rather than 5.
    assert parse_sic_code("9999 - Dormant company") == "9999"

def test_parse_sic_code_blank_and_placeholder():
    # "None Supplied" is the register's placeholder for no declared activity.
    assert parse_sic_code("") is None
    assert parse_sic_code(None) is None
    assert parse_sic_code("None Supplied") is None


# --- Industry fit ----------------------------------------------------------

def test_industry_fit_primary_code_scores_full():
    sics = ["41100 - Development of building projects", "", "", ""]
    assert industry_fit(sics) == 1.0

def test_industry_fit_secondary_code_is_discounted():
    # Same code, but declared as a secondary activity -> 1.00 * 0.80
    sics = ["56101 - Licensed restaurants", "41100 - Development of building projects", "", ""]
    assert industry_fit(sics) == pytest.approx(0.80)

def test_industry_fit_takes_the_best_match():
    # 68100 (0.70) beats 42990 (0.25); position 0 wins outright.
    sics = ["68100 - Buying and selling of own real estate", "42990 - Other civil engineering", "", ""]
    assert industry_fit(sics) == pytest.approx(0.70)

def test_industry_fit_unrelated_company_scores_zero():
    sics = ["62020 - Information technology consultancy", "", "", ""]
    assert industry_fit(sics) == 0.0


# --- Lifecycle -------------------------------------------------------------

def test_company_age_years():
    assert company_age_years(date(2016, 9, 1), AS_OF) == pytest.approx(10.0, abs=0.02)

def test_lifecycle_fit_too_young_scores_zero():
    # A developer with no completed scheme has no budget and no data need.
    assert lifecycle_fit(1.0) == 0.0

def test_lifecycle_fit_plateau_scores_full():
    # 4-9 years: multiple concurrent sites, no incumbent tool.
    assert lifecycle_fit(4.0) == 1.0
    assert lifecycle_fit(6.5) == 1.0
    assert lifecycle_fit(9.0) == 1.0

def test_lifecycle_fit_ramps_linearly():
    # Halfway between ramp start (2) and plateau start (4).
    assert lifecycle_fit(3.0) == pytest.approx(0.5)

def test_lifecycle_fit_decays_linearly():
    # Halfway between plateau end (9) and decay end (20).
    assert lifecycle_fit(14.5) == pytest.approx(0.5)

def test_lifecycle_fit_too_old_scores_zero():
    # Likely to have bought something already, and to have procurement.
    assert lifecycle_fit(25.0) == 0.0


# --- Filing health ---------------------------------------------------------

def test_filing_health_clean_company_scores_full():
    assert filing_health(date(2027, 3, 1), "FULL", date(2027, 1, 1), AS_OF) == 1.0

def test_filing_health_overdue_accounts_penalised():
    # Accounts due six months ago and still not filed.
    assert filing_health(date(2026, 3, 1), "FULL", date(2027, 1, 1), AS_OF) == pytest.approx(0.3)

def test_filing_health_dormant_penalised():
    # Dormant scores low for want of budget, not for bad management.
    assert filing_health(date(2027, 3, 1), "DORMANT", date(2027, 1, 1), AS_OF) == pytest.approx(0.5)

def test_filing_health_missing_due_date_is_not_a_penalty():
    # The register leaves this blank for companies too new to owe a filing.
    assert filing_health(None, "FULL", None, AS_OF) == 1.0

def test_filing_health_floors_at_zero():
    # Every penalty at once sums past 1.0; the score must not go negative.
    worst = filing_health(date(2020, 1, 1), "DORMANT", date(2020, 1, 1), AS_OF)
    assert worst == 0.0


# --- Commercial substance --------------------------------------------------

def test_substance_large_financed_developer_scores_full():
    # GROUP accounts (1.0) and three live charges (saturated at 1.0).
    assert commercial_substance("GROUP", 3) == pytest.approx(1.0)

def test_substance_micro_entity_with_no_charges_scores_low():
    # 0.65 * 0.20 + 0.35 * 0.0 — the dormant-adjacent shell case.
    assert commercial_substance("MICRO ENTITY", 0) == pytest.approx(0.13)

def test_substance_charges_saturate_at_three():
    # The gap between one site and three is commercially large; between
    # forty and forty-three it is not.
    assert commercial_substance("FULL", 3) == commercial_substance("FULL", 40)

def test_substance_unknown_category_scores_zero_on_size():
    # The register has a long tail of rare categories. A company we cannot
    # size must not outrank one we can.
    assert commercial_substance("SOME NEW CATEGORY", 0) == 0.0

def test_substance_handles_blank_and_non_numeric_charges():
    assert commercial_substance("SMALL", None) == pytest.approx(0.325)
    assert commercial_substance("SMALL", "") == pytest.approx(0.325)

def test_substance_size_outweighs_finance_activity():
    # A large developer with no live charges beats a micro-entity SPV with
    # three, which is the discrimination the component exists to make.
    assert commercial_substance("FULL", 0) > commercial_substance("MICRO ENTITY", 3)


# --- Total -----------------------------------------------------------------

def test_total_score_perfect_company():
    assert total_score(1.0, 1.0, 1.0, 1.0) == 100.0

def test_total_score_weights_sum_to_one_hundred():
    # Guards the invariant that makes the 0-100 scale meaningful.
    assert sum(config.WEIGHTS.values()) == 100

def test_total_score_wrong_industry_caps_at_sixty_five():
    # Industry fit is 35 points, so a perfect-but-irrelevant company cannot
    # outrank a good-fit one on the other three components alone.
    assert total_score(0.0, 1.0, 1.0, 1.0) == 65.0

def test_total_score_substance_breaks_the_tie_it_was_added_for():
    # The regression this component exists to prevent: two companies identical
    # on industry, lifecycle and filings must no longer score the same.
    big = total_score(1.0, 1.0, commercial_substance("FULL", 2), 1.0)
    small = total_score(1.0, 1.0, commercial_substance("MICRO ENTITY", 0), 1.0)
    assert big > small
