"""
pipeline.py
Score the filtered segment and write the ranked target list.

get_data.py decided *membership* — who is in the segment at all. This decides
*order*. Splitting them matters in practice: reweighting the score is a
five-second re-run, while re-filtering means re-reading two gigabytes.

Usage:  python pipeline.py
"""

import os
from datetime import date, datetime

import pandas as pd

import config
import scoring

SIC_COLUMNS = ["SICCode.SicText_1", "SICCode.SicText_2",
               "SICCode.SicText_3", "SICCode.SicText_4"]


def parse_uk_date(value):
    """Companies House publishes dates as DD/MM/YYYY. Blanks are common and
    meaningful — see the note on missing due dates in scoring.filing_health."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    text = str(value).strip()
    if not text or text.lower() == "nan":
        return None
    try:
        return datetime.strptime(text, "%d/%m/%Y").date()
    except ValueError:
        return None


def score_segment(segment, as_of):
    """Attach the three components and the total score to every row.

    Returned sorted by score descending. The component columns are kept rather
    than dropped: a salesperson who cannot see *why* a company ranks third will
    not trust the company ranked first.
    """
    rows = []
    for _, company in segment.iterrows():
        incorporated = parse_uk_date(company.get("IncorporationDate"))
        if incorporated is None:
            # Cannot age a company without an incorporation date, and the
            # lifecycle component is 40% of the score. Excluded rather than
            # guessed at.
            continue

        fit = scoring.industry_fit([company.get(c) for c in SIC_COLUMNS])
        age = scoring.company_age_years(incorporated, as_of)
        lifecycle = scoring.lifecycle_fit(age)
        health = scoring.filing_health(
            parse_uk_date(company.get("Accounts.NextDueDate")),
            company.get("Accounts.AccountCategory"),
            parse_uk_date(company.get("ConfStmtNextDueDate")),
            as_of,
        )

        substance = scoring.commercial_substance(
            company.get("Accounts.AccountCategory"),
            company.get("Mortgages.NumMortOutstanding"),
        )

        rows.append({
            "CompanyName": company["CompanyName"],
            "CompanyNumber": company["CompanyNumber"],
            "AddressLine1": company.get("RegAddress.AddressLine1"),
            "Postcode": company.get("RegAddress.PostCode"),
            "PostTown": company.get("RegAddress.PostTown"),
            "Incorporated": incorporated,
            "AgeYears": round(age, 1),
            "PrimarySIC": company.get("SICCode.SicText_1"),
            "AccountsCategory": company.get("Accounts.AccountCategory"),
            # Carried as context for the email, not scored — outstanding
            # charges on a developer are development finance, i.e. live sites.
            "MortgageCharges": company.get("Mortgages.NumMortCharges"),
            "MortgagesOutstanding": company.get("Mortgages.NumMortOutstanding"),
            "IndustryFit": round(fit, 3),
            "CommercialSubstance": round(substance, 3),
            "LifecycleFit": round(lifecycle, 3),
            "FilingHealth": round(health, 3),
            "Score": round(scoring.total_score(fit, lifecycle, substance, health), 1),
        })

    scored = pd.DataFrame(rows)
    return scored.sort_values("Score", ascending=False).reset_index(drop=True)


def group_key(name, address_line_1, postcode):
    """Identify companies that are almost certainly the same developer.

    Large developers incorporate one company per scheme — PEARL MK 340,
    PEARL LUTTERWORTH 4400, URBAN&CIVIC CORBY — all registered at the head
    office. These are special-purpose vehicles. You cannot sell to an SPV; the
    software decision sits with the parent, so five sibling SPVs in a top-25
    waste a salesperson's morning as surely as five dormant shells would.

    The key is (first word of the name, registered address). Address alone is
    not enough: company formation agents and accountants act as the registered
    office for thousands of unrelated companies, and collapsing those would
    merge genuinely distinct prospects. Requiring a shared name stem as well
    keeps the false-merge rate low at the cost of missing SPV families that
    are named inconsistently — the safer direction to err in.
    """
    stem = str(name or "").strip().upper().split()
    stem = stem[0] if stem else ""
    address = f"{str(address_line_1 or '').strip().upper()}|{str(postcode or '').strip().upper()}"
    return (stem, address)


def collapse_corporate_groups(scored):
    """Reduce each SPV family to its single best-scoring company.

    Adds `GroupCompanies`: how many companies the family contains. That count
    is not noise to be discarded — a developer running twelve SPVs from one
    office is running twelve schemes, which makes them a *larger* prospect and
    gives the opening line of an email something concrete to cite.
    """
    keyed = scored.copy()
    keyed["_key"] = [
        group_key(row["CompanyName"], row["AddressLine1"], row["Postcode"])
        for _, row in keyed.iterrows()
    ]
    sizes = keyed["_key"].value_counts()
    # Already sorted by score, so the first row of each group is its best.
    collapsed = keyed.drop_duplicates("_key", keep="first").copy()
    collapsed["GroupCompanies"] = collapsed["_key"].map(sizes).astype(int)
    return collapsed.drop(columns="_key").reset_index(drop=True)


def main():
    if not os.path.exists(config.SEGMENT_CSV):
        raise SystemExit(
            f"{config.SEGMENT_CSV} not found — run `python get_data.py` first."
        )

    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    segment = pd.read_csv(config.SEGMENT_CSV, dtype=str)
    print(f"Loaded {len(segment):,} companies in segment")

    # Scored as at the snapshot date, not today. Ages and overdue flags must
    # not drift every time the script is re-run against a fixed CSV.
    as_of = date.fromisoformat(config.SNAPSHOT_DATE)
    scored = score_segment(segment, as_of)

    accounts = collapse_corporate_groups(scored)
    print(f"Collapsed {len(scored):,} companies into {len(accounts):,} accounts "
          f"({len(scored) - len(accounts):,} sibling SPVs folded into parents)")

    full_path = os.path.join(config.OUTPUT_DIR, "scored_segment.csv")
    top_path = os.path.join(config.OUTPUT_DIR, f"top_{config.TOP_N}.csv")
    accounts.to_csv(full_path, index=False)
    accounts.head(config.TOP_N).to_csv(top_path, index=False)

    print(f"Ranked accounts -> {full_path}")
    print(f"Top {config.TOP_N} -> {top_path}")
    print()
    print(accounts.head(10)[["CompanyName", "AgeYears", "GroupCompanies", "Score"]]
          .to_string(index=False))


if __name__ == "__main__":
    main()
