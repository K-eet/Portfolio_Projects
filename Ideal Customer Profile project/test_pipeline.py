"""
test_pipeline.py
Unit tests for pipeline.py — date parsing and the end-to-end ranking, checked
on a small hand-built segment where the right answer is arguable in words.
"""

from datetime import date

import pandas as pd
import pytest

from pipeline import (parse_uk_date, score_segment,
                      group_key, collapse_corporate_groups)

AS_OF = date(2026, 9, 1)


# --- Date parsing ----------------------------------------------------------

def test_parse_uk_date_day_first():
    # 03/04/2019 is 3 April, not 4 March. Getting this backwards would silently
    # mis-age a third of the register.
    assert parse_uk_date("03/04/2019") == date(2019, 4, 3)

def test_parse_uk_date_blank_variants():
    assert parse_uk_date("") is None
    assert parse_uk_date(None) is None
    assert parse_uk_date("nan") is None

def test_parse_uk_date_malformed_returns_none():
    assert parse_uk_date("not a date") is None


# --- Ranking ---------------------------------------------------------------

def _company(name, number, sic, incorporated, accounts_due="01/03/2027",
             category="FULL", conf_due="01/01/2027"):
    return {
        "CompanyName": name,
        "CompanyNumber": number,
        "RegAddress.AddressLine1": "1 Example Street",
        "RegAddress.PostCode": "SW1A 1AA",
        "RegAddress.PostTown": "LONDON",
        "IncorporationDate": incorporated,
        "Accounts.NextDueDate": accounts_due,
        "Accounts.LastMadeUpDate": "01/03/2026",
        "Accounts.AccountCategory": category,
        "ConfStmtNextDueDate": conf_due,
        "Mortgages.NumMortCharges": "2",
        "Mortgages.NumMortOutstanding": "1",
        "SICCode.SicText_1": sic,
        "SICCode.SicText_2": "",
        "SICCode.SicText_3": "",
        "SICCode.SicText_4": "",
    }


DEVELOPER = "41100 - Development of building projects"
LETTINGS = "68209 - Other letting of own property"


def test_ideal_prospect_outranks_the_rest():
    # Six years old, right SIC, filings clean -> should be first.
    segment = pd.DataFrame([
        _company("Too Young Ltd", "111", DEVELOPER, "01/03/2025"),
        _company("Ideal Developments Ltd", "222", DEVELOPER, "01/03/2020"),
        _company("Wrong Sector Ltd", "333", LETTINGS, "01/03/2020"),
    ])
    ranked = score_segment(segment, AS_OF)
    assert ranked.iloc[0]["CompanyName"] == "Ideal Developments Ltd"
    # FULL accounts (0.90) with one live charge (1/3): substance 0.70 -> 17.5
    # of the 25-point band. 35 + 25 + 17.5 + 15 = 92.5, not a clean 100.
    assert ranked.iloc[0]["Score"] == pytest.approx(92.5, abs=0.1)

def test_overdue_accounts_demote_an_otherwise_perfect_company():
    segment = pd.DataFrame([
        _company("Clean Ltd", "111", DEVELOPER, "01/03/2020"),
        _company("Overdue Ltd", "222", DEVELOPER, "01/03/2020",
                 accounts_due="01/03/2026"),
    ])
    ranked = score_segment(segment, AS_OF)
    assert list(ranked["CompanyName"]) == ["Clean Ltd", "Overdue Ltd"]
    # 15-point health band, 70% of it deducted -> 10.5 points lost.
    gap = ranked.iloc[0]["Score"] - ranked.iloc[1]["Score"]
    assert gap == pytest.approx(10.5, abs=0.1)

def test_company_without_incorporation_date_is_excluded():
    # Age is 40% of the score; a missing date is dropped, not guessed.
    segment = pd.DataFrame([
        _company("Known Ltd", "111", DEVELOPER, "01/03/2020"),
        _company("Undated Ltd", "222", DEVELOPER, ""),
    ])
    ranked = score_segment(segment, AS_OF)
    assert list(ranked["CompanyName"]) == ["Known Ltd"]

def test_component_columns_are_preserved_for_inspection():
    # A score a salesperson cannot decompose is a score they will not trust.
    segment = pd.DataFrame([_company("Ideal Ltd", "111", DEVELOPER, "01/03/2020")])
    ranked = score_segment(segment, AS_OF)
    for column in ("IndustryFit", "LifecycleFit", "FilingHealth", "Score"):
        assert column in ranked.columns

def test_live_charges_lift_an_otherwise_identical_company():
    # Outstanding charges on a developer are development finance — evidence of
    # live sites — so they raise the score rather than reading as distress.
    financed = _company("Financed Ltd", "111", DEVELOPER, "01/03/2020")
    financed["Mortgages.NumMortOutstanding"] = "3"
    unfinanced = _company("Unfinanced Ltd", "222", DEVELOPER, "01/03/2020")
    unfinanced["Mortgages.NumMortOutstanding"] = "0"
    ranked = score_segment(pd.DataFrame([financed, unfinanced]), AS_OF)
    assert list(ranked["CompanyName"]) == ["Financed Ltd", "Unfinanced Ltd"]

def test_substance_column_is_preserved_for_inspection():
    segment = pd.DataFrame([_company("Ideal Ltd", "111", DEVELOPER, "01/03/2020")])
    assert "CommercialSubstance" in score_segment(segment, AS_OF).columns


# --- Corporate group collapsing --------------------------------------------

def test_group_key_matches_spv_siblings():
    # Same developer, one company per scheme, one registered office.
    a = group_key("PEARL MK 340 LIMITED", "10 Hanover Square", "W1S 1BJ")
    b = group_key("PEARL LUTTERWORTH 4400 LIMITED", "10 Hanover Square", "W1S 1BJ")
    assert a == b

def test_group_key_separates_unrelated_companies_at_one_address():
    # Formation agents are the registered office for thousands of unrelated
    # companies. Address alone would merge genuinely distinct prospects.
    a = group_key("ALPHA DEVELOPMENTS LTD", "1 Agent House", "EC1A 1AA")
    b = group_key("BETA HOMES LTD", "1 Agent House", "EC1A 1AA")
    assert a != b

def test_group_key_separates_same_stem_at_different_addresses():
    a = group_key("PEARL MK 340 LIMITED", "10 Hanover Square", "W1S 1BJ")
    b = group_key("PEARL HOMES LIMITED", "99 Other Road", "SE1 2AA")
    assert a != b

def test_collapse_keeps_the_best_scoring_sibling_and_counts_the_family():
    spv_a = _company("PEARL MK 340 LIMITED", "111", DEVELOPER, "01/03/2020")
    spv_b = _company("PEARL MK 330 LIMITED", "222", DEVELOPER, "01/03/2020")
    # Give the second SPV overdue accounts so the ranking is unambiguous.
    spv_b["Accounts.NextDueDate"] = "01/03/2026"
    other = _company("SOLO DEVELOPMENTS LTD", "333", DEVELOPER, "01/03/2020")
    other["RegAddress.AddressLine1"] = "99 Other Road"

    ranked = score_segment(pd.DataFrame([spv_a, spv_b, other]), AS_OF)
    accounts = collapse_corporate_groups(ranked)

    names = list(accounts["CompanyName"])
    assert "PEARL MK 340 LIMITED" in names
    assert "PEARL MK 330 LIMITED" not in names   # folded into its sibling
    assert "SOLO DEVELOPMENTS LTD" in names
    assert len(accounts) == 2

def test_collapse_reports_family_size_as_a_selling_signal():
    # Twelve SPVs means twelve live schemes — the count is the email's hook,
    # not a duplicate to be silently discarded.
    spvs = [_company(f"PEARL SITE {i} LIMITED", str(i), DEVELOPER, "01/03/2020")
            for i in range(12)]
    accounts = collapse_corporate_groups(score_segment(pd.DataFrame(spvs), AS_OF))
    assert len(accounts) == 1
    assert accounts.iloc[0]["GroupCompanies"] == 12
