"""
config.py
Single source of truth for the analysis window and company identifiers.

Every notebook imports from here. Previously each notebook defined its own
cutoff — notebooks 01/03/04 derived one from `datetime.today()` while notebook
05 hard-coded 2024 — so the window silently shifted every January while the
written analysis stayed pinned to the years it was drafted against.
"""

# The fiscal years this analysis covers. Fixed deliberately, not derived from
# today's date: the prose in notebooks 03-05 and the README argues about these
# specific years, so the data window must not move underneath it. Extending the
# analysis is an edit to this list plus a re-reading of the theses — not
# something that should happen on its own when a new 10-K is filed.
ANALYSIS_YEARS = [2022, 2023, 2024]
FIRST_YEAR = ANALYSIS_YEARS[0]
LAST_YEAR = ANALYSIS_YEARS[-1]

COMPANIES = ["Tesla", "BYD", "Ford"]

# SEC Central Index Keys. BYD is absent by necessity, not oversight: it files no
# financial reports with the SEC at all. Its only EDGAR presence (CIK 1445162)
# is ADR registration paperwork — F-6EF, F-6 POS, 424B3 — filed by the
# depositary bank, and data.sec.gov returns 404 for its companyfacts. See the
# data-source note in notebook 01.
CIKS = {"Tesla": "1318605", "Ford": "37996"}

# Tickers are needed for market prices (which EDGAR does not publish) and, for
# BYD, for the financial statements themselves.
TICKERS = {"Tesla": "TSLA", "BYD": "BYDDY", "Ford": "F"}

# Reporting currency of each company's financial statements. BYD reports in
# renminbi while its ADR trades in dollars — the single most consequential fact
# in this pipeline, and the source of a bug that made BYD look ~7x more cash
# generative and ~7x cheaper than it is.
REPORTING_CURRENCY = {"Tesla": "USD", "BYD": "CNY", "Ford": "USD"}

# Capex is booked under different XBRL tags by different filers.
CAPEX_TAG = {
    "Tesla": "PaymentsToAcquirePropertyPlantAndEquipment",
    "Ford": "PaymentsToAcquireProductiveAssets",
}

COLORS = {"Tesla": "#E31937", "BYD": "#1DB954", "Ford": "#003DA5"}
