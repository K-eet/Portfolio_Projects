"""Build the student-level analysis table from the raw OULAD tables.

The unit of analysis is one student on one module-presentation, which is the
grain of studentInfo.csv. Everything else is aggregated up to that grain.

Two decisions in this module carry most of the analytical weight, and both are
recorded in the exclusion log rather than applied quietly:

1. Early engagement is measured over days 0 to 29 inclusive. Clicks logged on
   negative dates, before the module opens, are not counted.
2. Students who unregistered before day 30 are marked outside the analysis
   sample. Their click window was cut short by the withdrawal itself, so for
   them low engagement is a consequence of the outcome rather than a
   predictor of it.

Run directly to build the table and print the exclusion log:

    python -m src.clean
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.data import load_all

# Ordered deprivation bands, least to most deprived area is 0-10% upward.
# Band 1 is written "10-20" in the raw file, with no percent sign.
IMD_ORDER = [
    "0-10%", "10-20%", "20-30%", "30-40%", "40-50%",
    "50-60%", "60-70%", "70-80%", "80-90%", "90-100%",
]

# The engagement window, in days from the start of the module-presentation.
EARLY_WINDOW = (0, 29)

# Background variables carried into the analysis table. The six controls named
# in CLAUDE.md rule 5, plus gender and region for the descriptive tables.
BACKGROUND = [
    "imd_band", "highest_education", "age_band", "disability",
    "num_of_prev_attempts", "studied_credits", "gender", "region",
]

# The six that enter the regression models.
CONTROLS = [
    "imd_band", "highest_education", "age_band", "disability",
    "num_of_prev_attempts", "studied_credits",
]

PASS_RESULTS = ["Pass", "Distinction"]


class ExclusionLog:
    """Record every row-count decision so none of them happens silently."""

    def __init__(self) -> None:
        self.entries: list[tuple[str, int, str]] = []

    def note(self, label: str, count: int, reason: str) -> None:
        self.entries.append((label, count, reason))

    def to_frame(self) -> pd.DataFrame:
        return pd.DataFrame(self.entries, columns=["step", "rows", "reason"])

    def __str__(self) -> str:
        width = max(len(e[0]) for e in self.entries)
        lines = []
        for label, count, reason in self.entries:
            lines.append(f"  {label:<{width}}  {count:>7,}   {reason}")
        return "\n".join(lines)


def clean_imd_band(series: pd.Series) -> pd.Series:
    """Normalise imd_band labels and return an ordered categorical.

    The raw column writes one band as "10-20" while the other nine end in a
    percent sign. Mapping against the clean labels without fixing this drops
    roughly 3,500 students into missing.
    """
    normalised = series.astype("string").str.strip()
    needs_suffix = normalised.notna() & ~normalised.str.endswith("%")
    normalised = normalised.mask(needs_suffix, normalised + "%")

    unexpected = set(normalised.dropna().unique()) - set(IMD_ORDER)
    if unexpected:
        raise ValueError(f"Unrecognised imd_band labels: {sorted(unexpected)}")

    return pd.Categorical(normalised, categories=IMD_ORDER, ordered=True)


def compute_early_clicks(
    student_vle: pd.DataFrame, window: tuple[int, int] = EARLY_WINDOW
) -> pd.DataFrame:
    """Total VLE clicks per student per module-presentation inside the window.

    Returns only students with at least one click in the window. Students with
    none are filled with zero when this is joined onto the student table.
    """
    low, high = window
    in_window = student_vle["date"].between(low, high)
    subset = student_vle.loc[in_window, :]
    grouped = (
        subset.assign(sum_click=subset["sum_click"].astype("int64"))
        .groupby(["code_module", "code_presentation", "id_student"], observed=True)[
            "sum_click"
        ]
        .sum()
        .rename("early_clicks")
        .reset_index()
    )
    return grouped


def compute_mean_score(
    student_assessment: pd.DataFrame,
    assessments: pd.DataFrame,
    exclude_banked: bool = True,
) -> pd.DataFrame:
    """Weighted mean assessment score per student per module-presentation.

    Each student's score is weighted by the assessment weight, so formative
    assessments with weight zero carry no influence. A student whose only
    submissions were formative has no weighted mean; the result is missing for
    them rather than zero, because they sat nothing that counted.
    """
    merged = student_assessment.merge(
        assessments[
            ["id_assessment", "code_module", "code_presentation", "weight"]
        ],
        on="id_assessment",
        how="left",
        validate="many_to_one",
    )

    if exclude_banked:
        merged = merged.loc[merged["is_banked"] == 0, :]

    merged = merged.loc[merged["score"].notna(), :]
    merged = merged.assign(weighted=merged["score"] * merged["weight"])

    totals = merged.groupby(
        ["code_module", "code_presentation", "id_student"], observed=True
    ).agg(weighted_sum=("weighted", "sum"), weight_sum=("weight", "sum"))

    # A zero weight total means no summative work; leave it missing.
    # Use where() rather than replace(0, pd.NA): replace produces an object
    # column, and dividing by it yields an object dtype that statsmodels
    # cannot fit.
    positive_weight = totals["weight_sum"].where(totals["weight_sum"] > 0)
    totals["mean_score"] = totals["weighted_sum"] / positive_weight
    return totals[["mean_score"]].reset_index()


def build_analysis_table(
    data_dir: Path | str = "data",
) -> tuple[pd.DataFrame, ExclusionLog]:
    """Assemble one row per student per module-presentation.

    No rows are removed. Rows that should not enter the regression are marked
    with in_analysis_sample = False and counted in the returned log.
    """
    tables = load_all(data_dir)
    log = ExclusionLog()

    info = tables["studentInfo"]
    log.note("studentInfo rows", len(info), "one row per student per presentation")

    df = info.merge(
        tables["studentRegistration"][
            ["code_module", "code_presentation", "id_student",
             "date_registration", "date_unregistration"]
        ],
        on=["code_module", "code_presentation", "id_student"],
        how="left",
        validate="one_to_one",
    )
    log.note("after registration join", len(df), "one-to-one, no rows gained or lost")

    # Early engagement. Absence of a VLE row means no clicks, which is zero.
    clicks = compute_early_clicks(tables["studentVle"])
    df = df.merge(
        clicks,
        on=["code_module", "code_presentation", "id_student"],
        how="left",
        validate="one_to_one",
    )
    no_clicks = int(df["early_clicks"].isna().sum())
    df["early_clicks"] = df["early_clicks"].fillna(0).astype("int64")
    log.note(
        "no clicks in days 0-29", no_clicks,
        "set to 0 clicks, not dropped and not missing",
    )

    # Attainment.
    scores = compute_mean_score(
        tables["studentAssessment"], tables["assessments"]
    )
    df = df.merge(
        scores,
        on=["code_module", "code_presentation", "id_student"],
        how="left",
        validate="one_to_one",
    )
    log.note(
        "no weighted mean score", int(df["mean_score"].isna().sum()),
        "sat no assessment that carried weight; left missing",
    )

    # Outcomes.
    df["withdrawn"] = (df["final_result"] == "Withdrawn").astype("int8")
    df["passed"] = df["final_result"].isin(PASS_RESULTS).astype("int8")

    # Background.
    df["imd_band"] = clean_imd_band(df["imd_band"])
    log.note(
        "imd_band missing", int(df["imd_band"].isna().sum()),
        "kept in the table; statsmodels drops them from the models",
    )

    # Module-presentation identifier, used as a fixed effect.
    df["module_presentation"] = (
        df["code_module"].astype(str) + "-" + df["code_presentation"].astype(str)
    )
    # Presentations ending B start in February, those ending J start in October.
    df["start_month"] = df["code_presentation"].astype(str).str[-1].map(
        {"B": "February", "J": "October"}
    )

    # The engagement window restriction required by CLAUDE.md rule 4.
    unreg = df["date_unregistration"]
    df["unregistered_before_window"] = (unreg < EARLY_WINDOW[0]).fillna(False)
    df["unregistered_during_window"] = (
        unreg.between(*EARLY_WINDOW)
    ).fillna(False)
    df["in_analysis_sample"] = ~(
        df["unregistered_before_window"] | df["unregistered_during_window"]
    )

    log.note(
        "unregistered before day 0", int(df["unregistered_before_window"].sum()),
        "no opportunity to click in the window; outside analysis sample",
    )
    log.note(
        "unregistered during days 0-29", int(df["unregistered_during_window"].sum()),
        "click window truncated by the withdrawal; outside analysis sample",
    )
    log.note(
        "analysis sample", int(df["in_analysis_sample"].sum()),
        "still registered at day 30",
    )

    return df, log


def main() -> None:
    df, log = build_analysis_table()
    print("Exclusion log\n")
    print(log)
    print(f"\nAnalysis table: {len(df):,} rows x {df.shape[1]} columns")
    print(f"Analysis sample: {int(df['in_analysis_sample'].sum()):,} rows")
    out = Path("data") / "analysis_table.csv"
    df.to_csv(out, index=False)
    print(f"\nCached to {out}")


if __name__ == "__main__":
    main()
