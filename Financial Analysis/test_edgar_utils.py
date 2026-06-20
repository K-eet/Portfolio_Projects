"""
test_edgar_utils.py
Unit tests for edgar_utils.py — verifies XBRL extraction logic
against small hand-built fixtures (no live API calls).
"""

import pandas as pd
import pytest

from edgar_utils import (
    get_full_metric_history,
    get_instant_metric_history,
    get_ytd_flow_history,
    get_merged_metric_history,
)


def _make_facts(concept, entries):
    """Wrap a list of unit entries in the nested companyfacts structure."""
    return {"facts": {"us-gaap": {concept: {"units": {"USD": entries}}}}}


def test_instant_returns_sorted_point_in_time_snapshots():
    # Instant (balance-sheet) entries have only an 'end' date, no 'start'.
    # Given out-of-order entries, we expect them sorted ascending by end date.
    facts = _make_facts("Assets", [
        {"end": "2023-09-30", "val": 300, "form": "10-Q", "filed": "2023-10-25"},
        {"end": "2023-03-31", "val": 100, "form": "10-Q", "filed": "2023-04-26"},
        {"end": "2023-06-30", "val": 200, "form": "10-Q", "filed": "2023-07-26"},
    ])

    result = get_instant_metric_history(facts, "Assets")

    assert list(result.columns) == ["end", "val"]
    assert result["val"].tolist() == [100, 200, 300]
    assert result["end"].tolist() == [
        pd.Timestamp("2023-03-31"),
        pd.Timestamp("2023-06-30"),
        pd.Timestamp("2023-09-30"),
    ]


def test_instant_dedupes_restatements_keeping_latest_filed():
    # Same balance-sheet date (2023-12-31) reported twice: first in the Q1 10-Q
    # of the next year (preliminary), then restated in the 10-K filed later.
    # We keep the most recently filed value.
    facts = _make_facts("Assets", [
        {"end": "2023-12-31", "val": 400, "form": "10-Q", "filed": "2024-04-24"},
        {"end": "2023-12-31", "val": 425, "form": "10-K", "filed": "2024-01-29"},
    ])

    result = get_instant_metric_history(facts, "Assets")

    assert len(result) == 1
    assert result["val"].iloc[0] == 400  # the later-filed value wins


def _ytd_entry(start, end, val, form, filed):
    return {"start": start, "end": end, "val": val, "form": form, "filed": filed}


def test_ytd_flow_differences_cumulative_periods_into_quarters():
    # Cash-flow statements report year-to-date: Q1=3mo, Q2-filing=6mo YTD,
    # Q3-filing=9mo YTD, 10-K=12mo. Discrete quarters come from differencing.
    facts = _make_facts("NetCashProvidedByUsedInOperatingActivities", [
        _ytd_entry("2023-01-01", "2023-03-31", 100, "10-Q", "2023-04-20"),  # Q1 3mo
        _ytd_entry("2023-01-01", "2023-06-30", 250, "10-Q", "2023-07-20"),  # H1 6mo
        _ytd_entry("2023-01-01", "2023-09-30", 400, "10-Q", "2023-10-20"),  # 9mo
        _ytd_entry("2023-01-01", "2023-12-31", 600, "10-K", "2024-01-29"),  # FY 12mo
    ])

    quarterly, annual = get_ytd_flow_history(
        facts, "NetCashProvidedByUsedInOperatingActivities")

    assert quarterly["end"].tolist() == [
        pd.Timestamp("2023-03-31"),
        pd.Timestamp("2023-06-30"),
        pd.Timestamp("2023-09-30"),
        pd.Timestamp("2023-12-31"),
    ]
    # 100, 250-100, 400-250, 600-400
    assert quarterly["val"].tolist() == [100, 150, 150, 200]
    # annual is the 12-month 10-K figure, unchanged
    assert annual["val"].tolist() == [600]


def test_ytd_flow_handles_year_missing_an_interim_period():
    # If a cumulative period is missing (e.g. no 9-month filing tagged),
    # we should still emit the quarters we can derive and not crash or
    # produce a wrong difference across the gap.
    facts = _make_facts("NetCashProvidedByUsedInOperatingActivities", [
        _ytd_entry("2023-01-01", "2023-03-31", 100, "10-Q", "2023-04-20"),  # Q1
        _ytd_entry("2023-01-01", "2023-06-30", 250, "10-Q", "2023-07-20"),  # H1
        # no 9-month period
        _ytd_entry("2023-01-01", "2023-12-31", 600, "10-K", "2024-01-29"),  # FY
    ])

    quarterly, annual = get_ytd_flow_history(
        facts, "NetCashProvidedByUsedInOperatingActivities")

    ends = quarterly["end"].tolist()
    # Q1 and Q2 are derivable; Q3/Q4 are not (gap), so they're omitted
    assert pd.Timestamp("2023-03-31") in ends
    assert pd.Timestamp("2023-06-30") in ends
    assert pd.Timestamp("2023-09-30") not in ends
    assert pd.Timestamp("2023-12-31") not in ends
    assert annual["val"].tolist() == [600]


def _q(start, end, val, filed):
    return {"start": start, "end": end, "val": val, "form": "10-Q", "filed": filed}


def test_ytd_flow_ignores_standalone_interim_period_at_same_quarter_end():
    # Real-data case (Ford 2024): the filer reports BOTH a 6-month YTD figure
    # AND a standalone 3-month Apr-Jun figure, both ending 2024-06-30. Only the
    # cumulative-from-fiscal-year-start period should drive reconstruction, so
    # we must not emit two June-30 rows.
    facts = _make_facts("NetCashProvidedByUsedInOperatingActivities", [
        _ytd_entry("2024-01-01", "2024-03-31", 100, "10-Q", "2024-04-20"),  # Q1 3mo YTD
        _ytd_entry("2024-04-01", "2024-06-30", 160, "10-Q", "2024-07-20"),  # standalone 3mo
        _ytd_entry("2024-01-01", "2024-06-30", 250, "10-Q", "2024-07-20"),  # H1 6mo YTD
    ])

    quarterly, _ = get_ytd_flow_history(
        facts, "NetCashProvidedByUsedInOperatingActivities")

    june = quarterly[quarterly["end"] == pd.Timestamp("2024-06-30")]
    assert len(june) == 1
    assert june["val"].iloc[0] == 150  # 250 (6mo YTD) - 100 (Q1), not the 160 interim


def test_full_history_no_duplicate_q4_when_discrete_q4_reported():
    # The 10-K reports a discrete Oct-Dec quarter AND the full year. The Q4
    # reconstruction (FY - Q1 - Q2 - Q3) must not ALSO be appended, or we'd
    # get two Dec-31 rows. The reported discrete Q4 (40) wins over the
    # reconstructed one (FY100 - (10+20+25) = 45).
    facts = {"facts": {"us-gaap": {"NetIncomeLoss": {"units": {"USD": [
        _q("2022-01-01", "2022-03-31", 10, "2022-04-20"),
        _q("2022-04-01", "2022-06-30", 20, "2022-07-20"),
        _q("2022-07-01", "2022-09-30", 25, "2022-10-20"),
        {"start": "2022-10-01", "end": "2022-12-31", "val": 40,
         "form": "10-K", "filed": "2023-01-29"},  # discrete reported Q4
        {"start": "2022-01-01", "end": "2022-12-31", "val": 100,
         "form": "10-K", "filed": "2023-01-29"},  # full year
    ]}}}}}

    quarterly, _ = get_full_metric_history(facts, "NetIncomeLoss")

    q4 = quarterly[quarterly["end"] == pd.Timestamp("2022-12-31")]
    assert len(q4) == 1
    assert q4["val"].iloc[0] == 40


def test_merged_combines_tags_and_skips_missing_concepts():
    # Mimics a revenue tag migration: "OldRev" covers early quarters, "NewRev"
    # covers later ones, with one overlapping quarter (identical value).
    # "Absent" isn't in the data and must be skipped without error.
    facts = {"facts": {"us-gaap": {
        "OldRev": {"units": {"USD": [
            _q("2020-01-01", "2020-03-31", 100, "2020-04-20"),
            _q("2020-04-01", "2020-06-30", 110, "2020-07-20"),
        ]}},
        "NewRev": {"units": {"USD": [
            _q("2020-04-01", "2020-06-30", 110, "2020-07-20"),  # overlap, same val
            _q("2020-07-01", "2020-09-30", 120, "2020-10-20"),
        ]}},
    }}}

    quarterly, _ = get_merged_metric_history(
        facts, ["OldRev", "NewRev", "Absent"])

    assert quarterly["end"].tolist() == [
        pd.Timestamp("2020-03-31"),
        pd.Timestamp("2020-06-30"),
        pd.Timestamp("2020-09-30"),
    ]
    assert quarterly["val"].tolist() == [100, 110, 120]
