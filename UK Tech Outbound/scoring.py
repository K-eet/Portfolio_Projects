"""
scoring.py
The lead score, as three independent components combined by a weighted sum.

Kept as pure functions over primitives rather than as DataFrame operations so
that each rule can be tested against a stated example — see test_scoring.py.
The score is a weighted rank, not a model. That is a deliberate choice, not a
shortcut: nobody has labelled which of these companies actually bought
anything, so there is no target variable to train against, and a fitted model
here would be a confident-looking guess. A transparent score a sales team will
argue with beats an opaque one they will ignore.
"""

import re
from datetime import date

import config

# SIC fields arrive as "41100 - Development of building projects".
_SIC_CODE = re.compile(r"^\s*(\d{4,5})")


def parse_sic_code(sic_text):
    """Extract the numeric SIC code from a Companies House SIC field.

    Returns None for blanks and for the "None Supplied" placeholder the
    register uses when a company has never declared an activity.
    """
    if not sic_text:
        return None
    match = _SIC_CODE.match(str(sic_text))
    return match.group(1) if match else None


def industry_fit(sic_texts, relevance=None, secondary_discount=None):
    """Score 0-1 on how closely the company's declared activity matches the buyer.

    `sic_texts` is the ordered list of SICCode.SicText_1..4. The best-matching
    code wins; codes outside slot 1 are discounted because they describe a
    secondary line of business rather than what the company mainly does.
    """
    relevance = relevance if relevance is not None else config.SIC_RELEVANCE
    discount = secondary_discount if secondary_discount is not None else config.SECONDARY_SIC_DISCOUNT

    best = 0.0
    for position, text in enumerate(sic_texts):
        code = parse_sic_code(text)
        if code is None or code not in relevance:
            continue
        value = relevance[code]
        if position > 0:
            value *= discount
        best = max(best, value)
    return best


def company_age_years(incorporation_date, as_of):
    """Age in years as a float. Negative dates are impossible but not rejected
    here — the loader filters them, and this stays a pure arithmetic helper."""
    return (as_of - incorporation_date).days / 365.25


def lifecycle_fit(age_years,
                  ramp_start=None, plateau_start=None,
                  plateau_end=None, decay_end=None):
    """Score 0-1 on company age, as a trapezoid.

    Zero below `ramp_start`, rising linearly to 1.0 at `plateau_start`, flat
    until `plateau_end`, then falling linearly to zero at `decay_end`. The
    reasoning behind each boundary is in config.py.
    """
    ramp_start = ramp_start if ramp_start is not None else config.AGE_RAMP_START
    plateau_start = plateau_start if plateau_start is not None else config.AGE_PLATEAU_START
    plateau_end = plateau_end if plateau_end is not None else config.AGE_PLATEAU_END
    decay_end = decay_end if decay_end is not None else config.AGE_DECAY_END

    if age_years <= ramp_start or age_years >= decay_end:
        return 0.0
    if age_years < plateau_start:
        return (age_years - ramp_start) / (plateau_start - ramp_start)
    if age_years <= plateau_end:
        return 1.0
    return (decay_end - age_years) / (decay_end - plateau_end)


def filing_health(accounts_next_due, accounts_category,
                  confirmation_next_due, as_of):
    """Score 0-1 on statutory filing punctuality, floored at zero.

    Starts at 1.0 and deducts. Overdue accounts are the heaviest deduction: a
    company that has stopped filing has usually stopped doing other things too.
    Dormant and never-filed companies score low because they have no budget,
    not because they are badly run.

    A missing due date is treated as *not* overdue. The register leaves the
    field blank for companies too newly incorporated to owe a filing yet, and
    penalising those would contradict the lifecycle component.
    """
    score = 1.0

    if accounts_next_due is not None and accounts_next_due < as_of:
        score -= config.OVERDUE_ACCOUNTS_PENALTY

    category = (accounts_category or "").strip().upper()
    if category in config.DORMANT_ACCOUNT_CATEGORIES:
        score -= config.DORMANT_PENALTY

    if confirmation_next_due is not None and confirmation_next_due < as_of:
        score -= config.OVERDUE_CONFIRMATION_PENALTY

    return max(0.0, score)


def commercial_substance(accounts_category, mortgages_outstanding,
                         size_share=None, saturation=None):
    """Score 0-1 on whether the company is substantial enough to be a buyer.

    Combines two proxies, because the free dataset publishes no turnover or
    headcount: the statutory accounts category as a size ladder, and the count
    of outstanding mortgage charges as a live-development-finance signal.

    An unrecognised or missing accounts category scores zero on the size half
    rather than raising — the register carries a long tail of rare categories,
    and a company we cannot size should not outrank one we can.
    """
    size_share = size_share if size_share is not None else config.SUBSTANCE_SIZE_SHARE
    saturation = saturation if saturation is not None else config.CHARGES_SATURATION

    category = (accounts_category or "").strip().upper()
    size = config.ACCOUNT_SIZE_SCORE.get(category, 0.0)

    try:
        charges = float(mortgages_outstanding or 0)
    except (TypeError, ValueError):
        charges = 0.0
    finance_activity = min(1.0, max(0.0, charges) / saturation)

    return size_share * size + (1.0 - size_share) * finance_activity


def total_score(fit, lifecycle, substance, health, weights=None):
    """Combine the four components into a 0-100 score.

    Components are each 0-1 and the weights sum to 100, so the result needs no
    normalisation — which is the point of keeping them on a common scale.
    """
    weights = weights if weights is not None else config.WEIGHTS
    return (
        fit * weights["industry_fit"]
        + lifecycle * weights["lifecycle_fit"]
        + substance * weights["commercial_substance"]
        + health * weights["filing_health"]
    )
