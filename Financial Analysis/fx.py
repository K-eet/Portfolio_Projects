"""
fx.py
Currency conversion for cross-company comparison.

Why this module exists
----------------------
BYD's financial statements are reported in renminbi, but its ADR (BYDDY) trades
in US dollars, and Tesla and Ford report in dollars. Comparing BYD's reported
figures with the other two directly — or dividing a dollar market cap by a
renminbi net income — silently mixes currencies. That bug made BYD's 2024 free
cash flow read as $36.1B rather than ~$5.0B, and its P/E as 2.4x rather than
~17.5x.

Which rate to use
-----------------
The choice is not cosmetic and follows the same flow/stock distinction that
governs the EDGAR extractors:

  * Flows (revenue, net income, cash flow, EBITDA) accrue across a whole year,
    so they are translated at that year's AVERAGE rate.
  * Stocks (assets, cash, debt) are single-instant balance-sheet snapshots, so
    they are translated at the YEAR-END rate.

This mirrors IAS 21 / ASC 830 translation practice. Ratios of two same-currency
quantities (net profit margin, ROA, cash conversion) are unaffected by the
choice, but any figure compared across companies in absolute dollars — and
every valuation multiple, which divides a dollar market cap by a reported
earnings figure — depends on it.
"""

import pandas as pd
import yfinance as yf

# yfinance quotes CNY=X as renminbi PER dollar, so conversion divides.
CNY_PER_USD_TICKER = "CNY=X"


def get_annual_rates(years, ticker=CNY_PER_USD_TICKER):
    """Daily FX history collapsed to one average and one year-end rate per year.

    Returns a DataFrame indexed by year with columns ['average', 'year_end'],
    quoted as units of foreign currency per USD.
    """
    start = f"{min(years) - 1}-12-01"
    end = f"{max(years) + 1}-01-15"
    history = yf.Ticker(ticker).history(start=start, end=end)["Close"]
    history.index = history.index.tz_localize(None)

    rows = {}
    for year in years:
        year_rates = history[history.index.year == year]
        if year_rates.empty:
            raise ValueError(f"No {ticker} rates returned for {year}")
        rows[year] = {
            "average": float(year_rates.mean()),
            "year_end": float(year_rates.iloc[-1]),
            "trading_days": int(len(year_rates)),
        }
    return pd.DataFrame(rows).T.rename_axis("Year")


def to_usd(value, year, rates, kind):
    """Translate one foreign-currency figure into USD.

    `kind` must be 'flow' (average rate) or 'stock' (year-end rate); there is no
    default, because picking the wrong one is exactly the error this module was
    written to prevent.
    """
    if kind == "flow":
        rate = rates.loc[year, "average"]
    elif kind == "stock":
        rate = rates.loc[year, "year_end"]
    else:
        raise ValueError(f"kind must be 'flow' or 'stock', got {kind!r}")
    return value / rate
