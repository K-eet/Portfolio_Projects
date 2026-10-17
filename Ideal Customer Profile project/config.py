"""
config.py
Single source of truth for the segment definition and the scoring weights.

Everything that decides *who we target* lives here, not in the pipeline. That
is deliberate: the engine is segment-agnostic, so pointing it at a different
buyer — construction SIC codes for a contech vendor, 62010 for horizontal SaaS
— is an edit to this file and a re-run of get_data.py, not a rewrite.
"""

# ---------------------------------------------------------------------------
# Who we are selling for
# ---------------------------------------------------------------------------
# The worked example is a land-sourcing / planning-data product sold to UK
# property developers (the segment LandTech, Orbital and Searchland compete in).
# Naming the vendor matters: a score is only defensible relative to a product.
VENDOR_PROFILE = "Land sourcing and planning intelligence, sold to UK property developers"

# ---------------------------------------------------------------------------
# Industry fit — SIC code relevance
# ---------------------------------------------------------------------------
# Relevance is graded, not binary. A company whose primary activity is
# "development of building projects" is the buyer; a general civil engineering
# contractor might occasionally develop, and is worth less of a salesperson's
# morning. Scoring these the same would rank the list badly while looking
# rigorous, which is the failure mode worth avoiding.
SIC_RELEVANCE = {
    "41100": 1.00,  # Development of building projects — the exact buyer
    "68100": 0.70,  # Buying and selling of own real estate — adjacent, often the same team
    "41201": 0.55,  # Construction of commercial buildings — builds, sometimes develops
    "41202": 0.55,  # Construction of domestic buildings
    "68209": 0.35,  # Letting of own property — holds land, rarely sources it
    "42990": 0.25,  # Other civil engineering — weak signal, kept to widen the funnel
}

# A code listed as SICCode.SicText_1 is the company's self-declared main
# activity. The same code appearing in slot 2-4 is a secondary line of
# business, so it gets discounted rather than dropped.
SECONDARY_SIC_DISCOUNT = 0.80

# ---------------------------------------------------------------------------
# Geography
# ---------------------------------------------------------------------------
# London postcode areas. Registered address is not operating address — see the
# limitations section of the README — but at segment scale it is the only
# location signal the free dataset carries.
LONDON_POSTCODE_AREAS = {"E", "EC", "N", "NW", "SE", "SW", "W", "WC"}

# ---------------------------------------------------------------------------
# Lifecycle — company age in years
# ---------------------------------------------------------------------------
# A trapezoid, not a threshold. The commercial argument, in order:
#   under 2   a developer with no completed scheme has no budget and no data need
#   2 to 4    ramping; interest rises as they start bidding on more than one site
#   4 to 9    the sweet spot: multiple concurrent sites, still running on
#             spreadsheets and a planning portal, no incumbent tool
#   9 to 20   decaying; increasingly likely to have bought something already,
#             and to have a procurement process that a first call cannot clear
# The audit that scoped this project suggested a 2-5 year window borrowed from
# generic SaaS scale-up targeting. It is widened here because development cycles
# are long: a housebuilder four years old may still be on its first scheme.
AGE_RAMP_START = 2.0
AGE_PLATEAU_START = 4.0
AGE_PLATEAU_END = 9.0
AGE_DECAY_END = 20.0

# ---------------------------------------------------------------------------
# Filing health
# ---------------------------------------------------------------------------
# A disqualifier layer, not a credit assessment. The only question being asked
# is "would a salesperson waste a morning on this company", and overdue
# statutory filings are the cheapest available proxy for a company that is
# dormant, distressed or a shell.
#
# Note that this component deliberately ignores mortgage charges, which are
# handled by commercial_substance below and with the opposite sign. The
# reasoning for that inversion is set out there.
DORMANT_ACCOUNT_CATEGORIES = {"DORMANT", "NO ACCOUNTS FILED"}
OVERDUE_ACCOUNTS_PENALTY = 0.7   # subtracted from a 1.0 base
DORMANT_PENALTY = 0.5
OVERDUE_CONFIRMATION_PENALTY = 0.3

# ---------------------------------------------------------------------------
# Commercial substance — can this company actually buy anything?
# ---------------------------------------------------------------------------
# Added after the first full run, which is worth recording rather than hiding:
# with only industry, lifecycle and filing health, 4,401 of the 156,107
# companies scored exactly 100.0. A "top 25" drawn from a 4,401-way tie is
# alphabetical noise wearing the costume of a ranking. The three original
# components describe whether a company is the *right sort*; none of them
# describe whether it is big enough to have a budget.
#
# The free dataset carries no turnover or headcount. Two usable proxies remain:
#
# 1. Accounts category. What a company is permitted to file is set by statutory
#    size thresholds, so the category is a coarse but genuine size ladder. A
#    developer filing FULL or GROUP accounts is materially larger than one
#    filing as a micro-entity.
ACCOUNT_SIZE_SCORE = {
    "GROUP": 1.00,                       # Consolidated — a parent with subsidiaries
    "FULL": 0.90,
    "MEDIUM": 0.90,
    "AUDITED ABRIDGED": 0.70,
    "UNAUDITED ABRIDGED": 0.60,
    "SMALL": 0.50,
    "TOTAL EXEMPTION FULL": 0.40,
    "AUDIT EXEMPTION SUBSIDIARY": 0.40,
    "MICRO ENTITY": 0.20,                # Under ~£632k turnover — rarely a buyer
    "DORMANT": 0.00,
    "NO ACCOUNTS FILED": 0.00,
}

# 2. Outstanding mortgage charges, read as a POSITIVE signal.
#
#    This inverts the standard convention and the inversion is deliberate.
#    Conventionally, charges registered at Companies House are a risk marker:
#    they are debt secured against company assets, they rank a new lender
#    behind existing secured creditors, and credit reference agencies read a
#    rising charge count as rising leverage. On a credit report, five
#    outstanding charges is bad news.
#
#    But this is not a credit assessment. The question here is "is this company
#    worth an hour of a salesperson's time", not "will this company repay a
#    loan", and charges point in opposite directions for those two questions.
#    Development finance is how property development is funded: each live charge
#    roughly corresponds to a site currently being built. A developer with five
#    live charges is a worse credit risk and a better prospect, and both of
#    those are true at once. A developer with none is usually dormant, tiny, or
#    holding land it is not developing.
#
#    The cost of the inversion, stated plainly: an over-leveraged developer
#    heading for administration looks identical to a busy one on this signal.
#    Filing health catches the subset that stops filing, but a company can be
#    distressed and still file on time. This score prioritises a call list; it
#    is not a qualification decision, and it should not be used as one where the
#    vendor carries payment risk.
#
#    Saturating at three: the difference between one site and three is
#    commercially large, between forty and forty-three is not.
CHARGES_SATURATION = 3.0

# Within the substance component, size carries more than finance activity: a
# large developer with no live charges is still a buyer, while a micro-entity
# with three charges is usually a special-purpose vehicle holding one site.
SUBSTANCE_SIZE_SHARE = 0.65

# ---------------------------------------------------------------------------
# Weights
# ---------------------------------------------------------------------------
# Four components, summing to 100. Kept transparent on purpose: a sales team
# will act on a score it can argue with, and will quietly ignore one it cannot.
#
# Industry fit stays the largest single weight because calling the wrong sort
# of company is the most expensive mistake available. Filing health is
# deliberately the smallest — it is a disqualifier, not a ranking signal, and
# it does most of its work by dragging dead companies down rather than by
# separating live ones.
WEIGHTS = {
    "industry_fit": 35,
    "lifecycle_fit": 25,
    "commercial_substance": 25,
    "filing_health": 15,
}

# ---------------------------------------------------------------------------
# Data source
# ---------------------------------------------------------------------------
# Companies House Free Company Data Product: a monthly snapshot of every
# company on the register. No API key, no rate limit, no terms that stop a
# reviewer re-running this.
SNAPSHOT_DATE = "2026-09-01"
BULK_URL = f"https://download.companieshouse.gov.uk/BasicCompanyDataAsOneFile-{SNAPSHOT_DATE}.zip"

RAW_DIR = "data"
SEGMENT_CSV = "data/segment.csv"
OUTPUT_DIR = "outputs"
TOP_N = 25
