"""
app.py
An interactive front end over the ranked target-account list.

The score is transparent on purpose — a sales team will act on a score it can
argue with — so this app lets a visitor do the arguing: move the four weights,
narrow the segment, and watch the call list re-order. It reads the output of
pipeline.py rather than re-running it, so it starts in seconds and needs no
download.

Usage:  streamlit run app.py
"""

import os

import pandas as pd
import streamlit as st

import config
import scoring

HERE = os.path.dirname(os.path.abspath(__file__))
SCORED_CSV = os.path.join(HERE, config.OUTPUT_DIR, "scored_segment.csv")

COMPONENTS = {
    # weight key          column in scored_segment.csv   label shown to the visitor
    "industry_fit":         ("IndustryFit",         "Industry fit"),
    "lifecycle_fit":        ("LifecycleFit",        "Lifecycle fit"),
    "commercial_substance": ("CommercialSubstance", "Commercial substance"),
    "filing_health":        ("FilingHealth",        "Filing health"),
}

COMPONENT_HELP = {
    "industry_fit": "Is this the right sort of company? Graded by SIC code, not binary.",
    "lifecycle_fit": "Are they at the stage where the problem bites? Peaks at 4–9 years old.",
    "commercial_substance": "Can they buy anything? Accounts size class plus live development finance.",
    "filing_health": "Would a salesperson waste a morning here? Overdue filings pull it down.",
}

COMPANY_URL = "https://find-and-update.company-information.service.gov.uk/company/{}"


@st.cache_data
def load_accounts():
    accounts = pd.read_csv(SCORED_CSV, dtype={"CompanyNumber": str})
    # "SW6 5BP" -> "SW": the postcode area, which is how config defines London.
    accounts["PostcodeArea"] = (
        accounts["Postcode"].fillna("").str.upper().str.extract(r"^([A-Z]+)")[0].fillna("")
    )
    accounts["SIC"] = accounts["PrimarySIC"].fillna("None supplied")
    accounts["MortgagesOutstanding"] = pd.to_numeric(
        accounts["MortgagesOutstanding"], errors="coerce").fillna(0).astype(int)
    accounts["DefaultRank"] = range(1, len(accounts) + 1)
    return accounts


def score_with(accounts, weights):
    """Re-total every account under the visitor's weights, using the model's own
    scoring.total_score so the app cannot drift from the pipeline."""
    return scoring.total_score(
        accounts["IndustryFit"], accounts["LifecycleFit"],
        accounts["CommercialSubstance"], accounts["FilingHealth"],
        weights=weights,
    )


def talking_points(row):
    """The concrete facts an opening line could cite — the same signals the
    three emails in notebook 4 are written from."""
    points = []
    if row["GroupCompanies"] > 1:
        points.append(f"**{row['GroupCompanies']} companies** registered at the same address "
                      "under the same name, most likely one SPV per scheme.")
    if row["MortgagesOutstanding"] > 0:
        plural = "s" if row["MortgagesOutstanding"] != 1 else ""
        points.append(f"**{row['MortgagesOutstanding']} outstanding charge{plural}**, usually "
                      "development finance, so roughly that many live sites.")
    points.append(f"Incorporated **{row['Incorporated']}** ({row['AgeYears']} years old), "
                  f"filing **{str(row['AccountsCategory']).lower()}** accounts.")
    return points


st.set_page_config(page_title="Who should we call first?", page_icon="🎯", layout="wide")

accounts = load_accounts()

vendor = config.VENDOR_PROFILE[0].lower() + config.VENDOR_PROFILE[1:]
st.title("Who should we call first?")
st.markdown(
    f"A target-account model over the Companies House register for a hypothetical vendor: "
    f"*{vendor}*. It narrows 5.7 million UK companies to "
    f"**{len(accounts):,} London-registered developer accounts** and ranks them by a "
    f"four-part score. **The weights are yours to argue with** — change them below and the "
    f"list re-orders; narrow the segment in the sidebar. "
    f"[How it works](https://github.com/K-eet/Portfolio_Projects/tree/main/UK%20Tech%20Outbound)"
)

# ---------------------------------------------------------------------------
# Weights — on the page rather than in the sidebar, which phones collapse
# ---------------------------------------------------------------------------
# Defaults live in session state only, so the reset button can overwrite them.
reset = st.session_state.pop("reset_weights", False)
for key, value in config.WEIGHTS.items():
    if reset or f"w_{key}" not in st.session_state:
        st.session_state[f"w_{key}"] = value

raw = {}
for column, (key, (_, label)) in zip(st.columns(4), COMPONENTS.items()):
    raw[key] = column.slider(label, 0, 100, step=5, key=f"w_{key}", help=COMPONENT_HELP[key])
total = sum(raw.values())

note, button = st.columns([3, 1])
if total not in (0, 100):
    note.caption(f"Your weights add up to {total}; they are rescaled to 100.")
if button.button("Reset to the model's weights", width="stretch"):
    st.session_state["reset_weights"] = True
    st.rerun()

if total == 0:
    st.error("At least one weight has to be above zero.")
    st.stop()
# Rescaled to sum to 100 so scores stay on the model's 0-100 scale.
weights = {key: value * 100 / total for key, value in raw.items()}

# ---------------------------------------------------------------------------
# Sidebar: segment filters
# ---------------------------------------------------------------------------
AGE_CAP = 40.0  # a handful of companies on the register are over a century old
with st.sidebar:
    st.header("Segment")
    areas = sorted(a for a in accounts["PostcodeArea"].unique() if a)
    chosen_areas = st.multiselect("London postcode area", areas, placeholder="All areas")
    sic_options = [s for s in accounts["SIC"].value_counts().index]
    chosen_sic = st.multiselect("Main activity (primary SIC code)", sic_options,
                                placeholder="All activities")
    age_range = st.slider("Company age (years)", 0.0, AGE_CAP, (0.0, AGE_CAP), step=0.5,
                          help=f"{AGE_CAP:.0f} means {AGE_CAP:.0f} and older.")
    live_finance_only = st.checkbox("Only companies with outstanding charges",
                                    help="Live development finance: roughly, sites being built now.")
    top_n = st.select_slider("Accounts to show", [10, 25, 50, 100, 250], value=config.TOP_N)

# ---------------------------------------------------------------------------
# Re-score, filter, rank
# ---------------------------------------------------------------------------
ranked = accounts.copy()
ranked["Score"] = score_with(ranked, weights).round(1)
ranked = ranked.sort_values(["Score", "DefaultRank"], ascending=[False, True])
ranked["Rank"] = range(1, len(ranked) + 1)
ranked["Moved"] = ranked["DefaultRank"] - ranked["Rank"]

view = ranked
if chosen_areas:
    view = view[view["PostcodeArea"].isin(chosen_areas)]
if chosen_sic:
    view = view[view["SIC"].isin(chosen_sic)]
youngest, oldest = age_range
view = view[view["AgeYears"] >= youngest]
if oldest < AGE_CAP:
    view = view[view["AgeYears"] <= oldest]
if live_finance_only:
    view = view[view["MortgagesOutstanding"] > 0]

if view.empty:
    st.warning("No accounts match those filters.")
    st.stop()

shortlist = view.head(top_n)
reweighted = any(raw[k] * 100 / total != v for k, v in config.WEIGHTS.items())

c1, c2, c3 = st.columns(3)
c1.metric("Accounts in your segment", f"{len(view):,}")
c2.metric(f"Median score, top {len(shortlist)}", f"{shortlist['Score'].median():.1f}")
new_entries = int((shortlist["DefaultRank"] > top_n).sum()) if reweighted else 0
c3.metric(f"New to the top {top_n} under your weights", new_entries,
          help="Accounts in your shortlist that would not make the same-sized list "
               "under the model's default weights, before filtering.")

# ---------------------------------------------------------------------------
# The call list
# ---------------------------------------------------------------------------
st.subheader(f"Call order — top {len(shortlist)}")
table = shortlist.assign(
    Link=shortlist["CompanyNumber"].map(COMPANY_URL.format),
    Activity=shortlist["SIC"].str.replace(r"^\d+\s*-\s*", "", regex=True),
)[["Rank", "Moved", "CompanyName", "Score", "IndustryFit", "LifecycleFit",
   "CommercialSubstance", "FilingHealth", "AgeYears", "GroupCompanies",
   "MortgagesOutstanding", "Postcode", "Activity", "Link"]]

component_bar = dict(min_value=0.0, max_value=1.0, format="%.2f")
st.dataframe(
    table,
    hide_index=True,
    width="stretch",
    column_config={
        "Rank": st.column_config.NumberColumn("Rank", help="Rank across all accounts under your weights"),
        "Moved": st.column_config.NumberColumn(
            "Moved", format="%+d", help="Places gained (+) or lost (−) against the model's default weights"),
        "CompanyName": st.column_config.TextColumn("Company", width="medium"),
        "Activity": st.column_config.TextColumn("Activity", width="small"),
        "Score": st.column_config.ProgressColumn("Score", min_value=0, max_value=100, format="%.1f"),
        "IndustryFit": st.column_config.ProgressColumn("Industry", **component_bar),
        "LifecycleFit": st.column_config.ProgressColumn("Lifecycle", **component_bar),
        "CommercialSubstance": st.column_config.ProgressColumn("Substance", **component_bar),
        "FilingHealth": st.column_config.ProgressColumn("Filing", **component_bar),
        "AgeYears": st.column_config.NumberColumn("Age", format="%.1f"),
        "GroupCompanies": st.column_config.NumberColumn("Group", help="Companies in the SPV family"),
        "MortgagesOutstanding": st.column_config.NumberColumn("Live charges"),
        "Link": st.column_config.LinkColumn("Register", display_text="Open ↗"),
    },
)
st.download_button(
    "Download this list (CSV)",
    shortlist.drop(columns=["PostcodeArea", "SIC"]).to_csv(index=False),
    file_name="call_list.csv",
    mime="text/csv",
)

# ---------------------------------------------------------------------------
# Why is this company here?
# ---------------------------------------------------------------------------
st.subheader("Why is this company here?")
pick = st.selectbox("Pick an account from the list", shortlist["CompanyName"].tolist())
row = shortlist[shortlist["CompanyName"] == pick].iloc[0]

left, right = st.columns([3, 2])
with left:
    breakdown = pd.DataFrame({
        "Component": [label for _, label in COMPONENTS.values()],
        "Score (0–1)": [row[col] for col, _ in COMPONENTS.values()],
        "Weight": [round(weights[k], 1) for k in COMPONENTS],
    })
    breakdown["Points"] = (breakdown["Score (0–1)"] * breakdown["Weight"]).round(1)
    st.dataframe(breakdown, hide_index=True, width="stretch")
    st.caption(f"{row['Score']:.1f} points in total — rank {row['Rank']:,} of {len(ranked):,}.")
with right:
    st.markdown("**What an opening line could cite**")
    for point in talking_points(row):
        st.markdown(f"- {point}")
    st.markdown(f"[View on Companies House ↗]({COMPANY_URL.format(row['CompanyNumber'])})")

with st.expander("What this is not"):
    st.markdown(
        "- **A prioritisation, not a qualification.** Outstanding charges are read as a *positive* "
        "signal — live development finance — which inverts the credit-risk convention. A busy "
        "developer and an over-leveraged one look the same here, so keep payment-risk checks separate.\n"
        "- **No revenue data.** Companies House publishes no turnover for small companies; size is "
        "inferred from the accounts category.\n"
        "- **Registered address is not trading address**, and SIC codes are self-declared.\n"
        "- **SPV families were collapsed under the model's default weights**, so each family is "
        "represented by the company that scored best under those weights.\n\n"
        f"Data: Companies House Free Company Data Product, snapshot {config.SNAPSHOT_DATE}. "
        "Contains public sector information licensed under the Open Government Licence v3.0."
    )
