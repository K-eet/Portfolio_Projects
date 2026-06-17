"""
metrics.py
Core financial metric calculations for EV Financial Health Dashboard.
Centralizing these here ensures consistency across all notebooks.
"""

def net_profit_margin(net_income, revenue):
    """Net Profit Margin = Net Income / Revenue * 100"""
    return (net_income / revenue) * 100


def return_on_assets(net_income, total_assets):
    """Return on Assets = Net Income / Total Assets * 100"""
    return (net_income / total_assets) * 100


def cash_conversion_ratio(operating_cash_flow, net_income):
    """Cash Conversion Ratio = Operating Cash Flow / Net Income
    
    Ratio below 1.0 indicates the company reports more profit than 
    it generates in cash — a potential earnings quality red flag.
    """
    return operating_cash_flow / net_income


def price_to_earnings(market_cap, net_income):
    """P/E Ratio = Market Cap / Net Income
    
    Returns None if net income is not positive — a negative P/E 
    is mathematically valid but analytically meaningless.
    """
    if net_income <= 0:
        return None
    return market_cap / net_income


def fcf_yield(free_cash_flow, market_cap):
    """FCF Yield = Free Cash Flow / Market Cap * 100"""
    return (free_cash_flow / market_cap) * 100


def ev_to_ebitda(market_cap, total_debt, cash, ebitda):
    """EV/EBITDA = (Market Cap + Total Debt - Cash) / EBITDA
    
    Returns None if EBITDA is not positive.
    """
    if ebitda <= 0:
        return None
    enterprise_value = market_cap + total_debt - cash
    return enterprise_value / ebitda