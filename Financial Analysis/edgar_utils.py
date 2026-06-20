"""
edgar_utils.py
Functions for pulling and reconstructing quarterly financial data 
from SEC EDGAR's XBRL API.
"""

import requests
import pandas as pd

HEADERS = {
    "User-Agent": "Personal Portfolio Project keet@example.com"
}

def get_company_facts(cik):
    """Fetch all XBRL facts for a company by CIK."""
    cik_padded = str(cik).zfill(10)
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik_padded}.json"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()


def get_full_metric_history(facts, concept):
    """
    Extract complete quarterly (with reconstructed Q4) and annual 
    history for a given XBRL concept.
    """
    entries = facts['facts']['us-gaap'][concept]['units']['USD']
    df = pd.DataFrame(entries)
    df['start'] = pd.to_datetime(df['start'])
    df['end'] = pd.to_datetime(df['end'])
    df['duration_days'] = (df['end'] - df['start']).dt.days
    
    quarterly = df[(df['duration_days'] >= 80) & (df['duration_days'] <= 100)]
    quarterly = quarterly.sort_values('filed').drop_duplicates(subset=['end'], keep='last')
    quarterly = quarterly[['end', 'val']].sort_values('end').reset_index(drop=True)
    
    annual = df[(df['duration_days'] >= 350) & (df['duration_days'] <= 380)]
    annual = annual[annual['form'] == '10-K']
    annual = annual.sort_values('filed').drop_duplicates(subset=['end'], keep='last')
    annual = annual[['end', 'val']].sort_values('end').reset_index(drop=True)
    
    # Years where a discrete Q4 (Oct-Dec) is already reported directly,
    # usually in the 10-K. For these we keep the reported figure and skip
    # reconstruction, otherwise we'd emit two Dec-31 rows for the year.
    reported_q4_years = set(
        quarterly[quarterly['end'].dt.month == 12]['end'].dt.year
    )

    q4_rows = []
    for year in annual['end'].dt.year.unique():
        if year in reported_q4_years:
            continue
        annual_val = annual[annual['end'].dt.year == year]['val']
        if annual_val.empty:
            continue
        annual_val = annual_val.values[0]

        q1_q3_subset = quarterly[
            (quarterly['end'].dt.year == year) &
            (quarterly['end'].dt.month != 12)
        ]

        if q1_q3_subset.shape[0] == 3:
            q4_val = annual_val - q1_q3_subset['val'].sum()
            q4_date = pd.Timestamp(year=year, month=12, day=31)
            q4_rows.append({'end': q4_date, 'val': q4_val})
    
    q4_df = pd.DataFrame(q4_rows)
    full_quarterly = pd.concat([quarterly, q4_df]).sort_values('end').reset_index(drop=True)

    return full_quarterly, annual


def get_instant_metric_history(facts, concept):
    """
    Extract point-in-time history for an "instant" XBRL concept
    (balance-sheet items like Assets).

    Instant concepts are *stocks* measured at a single moment, so each
    entry has only an 'end' date — no 'start'/duration. Unlike flow
    concepts there's no Q4 to reconstruct: the year-end snapshot is
    reported directly in the 10-K (and the following Q1 10-Q).

    Returns a single DataFrame [end, val] of every reported period-end
    snapshot, deduplicated by 'end' keeping the most recently filed
    value (so restatements supersede earlier figures).
    """
    entries = facts['facts']['us-gaap'][concept]['units']['USD']
    df = pd.DataFrame(entries)
    df['end'] = pd.to_datetime(df['end'])

    df = df.sort_values('filed').drop_duplicates(subset=['end'], keep='last')
    return df[['end', 'val']].sort_values('end').reset_index(drop=True)


def get_ytd_flow_history(facts, concept):
    """
    Extract quarterly history for a flow concept that is reported
    year-to-date (cumulative), such as cash-flow-statement items like
    NetCashProvidedByUsedInOperatingActivities.

    Unlike the income statement (which reports each standalone 3-month
    quarter), the cash-flow statement in a 10-Q reports the period
    cumulative from the start of the fiscal year: Q1 is 3 months, the Q2
    filing is 6-month YTD, Q3 is 9-month YTD, and the 10-K is 12 months.
    Discrete quarters are recovered by differencing consecutive cumulative
    periods: Q2 = 6mo - Q1, Q3 = 9mo - 6mo, Q4 = FY - 9mo.

    Returns (quarterly, annual) DataFrames of [end, val], mirroring
    get_full_metric_history so callers can treat the two interchangeably.
    """
    entries = facts['facts']['us-gaap'][concept]['units']['USD']
    df = pd.DataFrame(entries)
    df['start'] = pd.to_datetime(df['start'])
    df['end'] = pd.to_datetime(df['end'])
    df['duration_days'] = (df['end'] - df['start']).dt.days

    # Map each cumulative period to how many quarters it spans (1=3mo .. 4=FY).
    def quarters_covered(days):
        if 80 <= days <= 100:
            return 1
        if 170 <= days <= 190:
            return 2
        if 260 <= days <= 285:
            return 3
        if 350 <= days <= 380:
            return 4
        return None

    # Which fiscal quarter the period ENDS in (calendar-year filers only:
    # both Tesla and Ford report on a Dec-31 fiscal year).
    df['q_end'] = df['end'].dt.month // 3
    df['q_span'] = df['duration_days'].apply(quarters_covered)

    # Keep only genuine year-to-date periods: a cumulative period ending at
    # quarter N must span exactly N quarters from the fiscal-year start. This
    # excludes standalone interim periods (e.g. a 3-month Apr-Jun figure that
    # also ends in Q2 but only spans one quarter).
    df = df[df['q_span'] == df['q_end']]
    df['fy'] = df['end'].dt.year

    # One cumulative value per (year, quarter), latest filing wins.
    df = df.sort_values('filed').drop_duplicates(
        subset=['fy', 'q_end'], keep='last')
    df = df.rename(columns={'q_end': 'q_covered'})

    q_rows = []
    a_rows = []
    for year, grp in df.groupby('fy'):
        cum = grp.set_index('q_covered')
        if 4 in cum.index:
            a_rows.append({'end': cum.loc[4, 'end'], 'val': cum.loc[4, 'val']})
        prev_val = 0
        prev_n = 0
        for n in [1, 2, 3, 4]:
            if n not in cum.index:
                continue
            # Only difference against the immediately preceding period; a gap
            # (prev_n != n-1) would span more than one quarter, so skip it.
            if n - prev_n == 1:
                q_rows.append({
                    'end': cum.loc[n, 'end'],
                    'val': cum.loc[n, 'val'] - prev_val,
                })
            prev_val = cum.loc[n, 'val']
            prev_n = n

    quarterly = pd.DataFrame(q_rows, columns=['end', 'val']).sort_values(
        'end').reset_index(drop=True)
    annual = pd.DataFrame(a_rows, columns=['end', 'val']).sort_values(
        'end').reset_index(drop=True)
    return quarterly, annual


def get_merged_metric_history(facts, concepts):
    """
    Extract a discrete-quarter metric that spans more than one XBRL concept
    tag, e.g. Revenue, where Ford reports 'Revenues' for older periods and
    'RevenueFromContractWithCustomerExcludingAssessedTax' after the ASC 606
    accounting-standard change. Earlier-listed concepts take precedence in
    any overlap; concepts absent from the data are skipped.

    Returns (quarterly, annual) DataFrames of [end, val], like
    get_full_metric_history.
    """
    q_parts, a_parts = [], []
    available = facts['facts']['us-gaap']
    for concept in concepts:
        if concept not in available:
            continue
        q, a = get_full_metric_history(facts, concept)
        q_parts.append(q)
        a_parts.append(a)

    def _merge(parts):
        if not parts:
            return pd.DataFrame(columns=['end', 'val'])
        merged = pd.concat(parts)
        # concat order follows `concepts`, so keep='first' honours precedence
        merged = merged.drop_duplicates(subset=['end'], keep='first')
        return merged.sort_values('end').reset_index(drop=True)

    return _merge(q_parts), _merge(a_parts)