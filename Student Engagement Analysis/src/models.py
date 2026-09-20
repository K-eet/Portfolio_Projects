"""Regression models linking early VLE engagement to continuation and attainment.

Three models are fitted on the analysis sample, pooled across modules with a
fixed effect for each module-presentation. The fixed effect absorbs every
difference between modules and between February and October starts, so the
engagement coefficient is identified from comparisons within a presentation
rather than across them.

Standard errors are clustered by student, because 19 percent of rows come from
students who sit more than one module and their outcomes are not independent.

Engagement enters as clicks per 100, so the reported odds ratio is the change
associated with 100 extra clicks in the first 30 days.

Run directly to fit everything and print the tables:

    python -m src.models
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

from src.clean import build_analysis_table

# Engagement is expressed per 100 clicks so the coefficient is readable.
CLICK_UNIT = 100

CONTROL_TERMS = [
    "C(imd_band)",
    "C(highest_education)",
    "C(age_band)",
    "C(disability)",
    "num_of_prev_attempts",
    "studied_credits",
]

FIXED_EFFECT = "C(module_presentation)"

MODEL_VARS = [
    "early_clicks_100", "imd_band", "highest_education", "age_band",
    "disability", "num_of_prev_attempts", "studied_credits",
    "module_presentation", "id_student",
]

# Click levels used for the predicted-probability table.
PREDICT_AT = [0, 100, 200, 400, 800]


def prepare(df: pd.DataFrame) -> pd.DataFrame:
    """Restrict to the analysis sample and add the scaled engagement measure."""
    sample = df.loc[df["in_analysis_sample"]].copy()
    sample["early_clicks_100"] = sample["early_clicks"] / CLICK_UNIT
    return sample


def _formula(outcome: str) -> str:
    terms = ["early_clicks_100", *CONTROL_TERMS, FIXED_EFFECT]
    return f"{outcome} ~ " + " + ".join(terms)


def _complete_cases(sample: pd.DataFrame, outcome: str) -> pd.DataFrame:
    """Drop rows missing anything the model needs, so clusters stay aligned."""
    needed = [outcome, *MODEL_VARS]
    return sample.dropna(subset=needed)


def fit(sample: pd.DataFrame, outcome: str, kind: str):
    """Fit one model with student-clustered standard errors."""
    data = _complete_cases(sample, outcome)
    model = smf.logit if kind == "logit" else smf.ols
    fitted = model(_formula(outcome), data=data).fit(
        cov_type="cluster",
        cov_kwds={"groups": data["id_student"]},
        disp=0,
    )
    return fitted, data


def odds_ratio_table(result, terms: list[str] | None = None) -> pd.DataFrame:
    """Odds ratios with 95 percent confidence intervals."""
    params = result.params
    conf = result.conf_int()
    table = pd.DataFrame(
        {
            "odds_ratio": np.exp(params),
            "ci_low": np.exp(conf[0]),
            "ci_high": np.exp(conf[1]),
            "p_value": result.pvalues,
        }
    )
    if terms is not None:
        table = table.loc[table.index.isin(terms)]
    return table.round(3)


def coefficient_table(result, terms: list[str] | None = None) -> pd.DataFrame:
    """Raw coefficients with confidence intervals, for the linear model."""
    conf = result.conf_int()
    table = pd.DataFrame(
        {
            "coefficient": result.params,
            "ci_low": conf[0],
            "ci_high": conf[1],
            "p_value": result.pvalues,
        }
    )
    if terms is not None:
        table = table.loc[table.index.isin(terms)]
    return table.round(3)


def reported_terms(result) -> list[str]:
    """Every term except the module-presentation fixed effects."""
    return [n for n in result.params.index if "module_presentation" not in n]


def predicted_at_click_levels(result, data: pd.DataFrame) -> pd.DataFrame:
    """Recycled predictions, the equivalent of Stata's margins command.

    Every student is assigned each click level in turn, keeping their real
    background and module, and the predictions are averaged. This gives the
    rate the model expects for the actual student population at that level of
    engagement, not for an artificial average student.
    """
    rows = []
    for level in PREDICT_AT:
        counterfactual = data.copy()
        counterfactual["early_clicks_100"] = level / CLICK_UNIT
        rows.append(
            {
                "early_clicks": level,
                "predicted": float(result.predict(counterfactual).mean()),
            }
        )
    return pd.DataFrame(rows)


def engagement_quintile_model(sample: pd.DataFrame, outcome: str, kind: str):
    """Refit with engagement as quintiles, to show the shape of the pattern.

    A single linear term assumes each extra 100 clicks matters as much as the
    last. Quintiles let the data say otherwise.
    """
    data = _complete_cases(sample, outcome).copy()
    data["engagement_quintile"] = pd.qcut(
        data["early_clicks"], 5,
        labels=["Q1 lowest", "Q2", "Q3", "Q4", "Q5 highest"],
        duplicates="drop",
    )
    terms = ["C(engagement_quintile)", *CONTROL_TERMS, FIXED_EFFECT]
    formula = f"{outcome} ~ " + " + ".join(terms)
    model = smf.logit if kind == "logit" else smf.ols
    return model(formula, data=data).fit(
        cov_type="cluster", cov_kwds={"groups": data["id_student"]}, disp=0
    )


def main() -> None:
    df, _ = build_analysis_table()
    sample = prepare(df)

    specs = [
        ("withdrawn", "logit", "Model 1: withdrawal"),
        ("passed", "logit", "Model 2: pass or distinction"),
        ("mean_score", "ols", "Model 3: mean weighted score"),
    ]

    for outcome, kind, title in specs:
        result, data = fit(sample, outcome, kind)
        print("=" * 72)
        print(f"{title}   ({kind.upper()}, n = {int(result.nobs):,})")
        print("=" * 72)

        terms = reported_terms(result)
        if kind == "logit":
            print("\nOdds ratios (95% CI), module-presentation effects omitted\n")
            print(odds_ratio_table(result, terms).to_string())
            print("\nPredicted rate at each level of early engagement\n")
            preds = predicted_at_click_levels(result, data)
            preds["predicted"] = (preds["predicted"] * 100).round(1)
            print(preds.rename(columns={"predicted": "predicted_pct"}).to_string(index=False))
        else:
            print("\nCoefficients in marks (95% CI), fixed effects omitted\n")
            print(coefficient_table(result, terms).to_string())
            print(f"\nR-squared: {result.rsquared:.3f}")

        quint = engagement_quintile_model(sample, outcome, kind)
        q_terms = [n for n in quint.params.index if "engagement_quintile" in n]
        print("\nEngagement quintiles (reference is Q1, the lowest fifth)\n")
        if kind == "logit":
            print(odds_ratio_table(quint, q_terms).to_string())
        else:
            print(coefficient_table(quint, q_terms).to_string())
        print()


if __name__ == "__main__":
    main()
