"""
score.py
Compute weighted scores for the Acquirepad UK target list and rank it.

The CSV holds the hand-scored evidence (0 to 3 per dimension, with sources).
This script holds the weights, checks the evidence rule, and writes the
ranking. Changing a weight is an edit here and a re-run, nothing else.

Usage:  python score.py
"""

import csv
import os

HERE = os.path.dirname(os.path.abspath(__file__))
TARGETS_CSV = os.path.join(HERE, "data", "uk_targets.csv")
RANKED_CSV = os.path.join(HERE, "outputs", "ranked.csv")

# Weights sum to 100, so a firm scoring 3 on every dimension totals 100.
# The reasoning for each is in icp.md.
WEIGHTS = {
    "segment": 15,
    "size": 10,
    "deal_flow": 15,
    "operating_breadth": 20,
    "trigger": 20,
    "warm_path": 20,
}
MAX_SCORE = 3

# Trigger is built from parts rather than scored directly: an event (0-2), plus a
# point for active capital and a point for a data, digital or innovation hire,
# capped at MAX_SCORE. Each part is a CSV column with its own source tag.
TRIGGER_PARTS = {
    "trigger_event": ("trigger_event", 2),
    "trigger_active_capital": ("active_capital", 1),
    "trigger_data_hire": ("data_hire", 1),
}

# Unscored columns: the first move for each firm and its known property systems.
TEXT_FACTS = ["first_move", "systems"]


def weighted_total(scores, weights=WEIGHTS):
    """Combine 0-3 dimension scores into a 0-100 total."""
    return sum(weights[d] * scores[d] / MAX_SCORE for d in weights)


def trigger_score(row):
    """Sum the trigger parts, capped at MAX_SCORE."""
    return min(MAX_SCORE, sum(int(row[col]) for col in TRIGGER_PARTS))


def evidence_items(row, weights=WEIGHTS):
    """Yield (source tag, score, max) for everything that needs evidence.

    Directly scored dimensions use their own name as the tag. Trigger is
    checked part by part, because that is where the evidence attaches.
    """
    for dim in weights:
        if dim != "trigger":
            yield dim, int(row[f"score_{dim}"]), MAX_SCORE
    for col, (tag, cap) in TRIGGER_PARTS.items():
        yield tag, int(row[col]), cap


def parse_sources(text):
    """Turn 'deal_flow: url ; url | trigger: url' into {dimension: [urls]}."""
    sources = {}
    for block in filter(None, (b.strip() for b in (text or "").split("|"))):
        dim, _, urls = block.partition(":")
        sources[dim.strip()] = [u.strip() for u in urls.split(";") if u.strip()]
    return sources


def check_row(row, weights=WEIGHTS):
    """Return a list of rule breaches for one firm. Empty means the row is valid.

    The rule from the brief: every score above 0 needs at least one source URL,
    and anything that cannot be sourced scores 0 and is listed as unverified.
    """
    problems = []
    sources = parse_sources(row["sources"])
    unverified = set(filter(None, row.get("unverified", "").split(";")))
    for tag, score, cap in evidence_items(row, weights):
        if not 0 <= score <= cap:
            problems.append(f"{tag} score {score} is outside 0-{cap}")
        urls = [u for u in sources.get(tag, []) if u.startswith("http")]
        if score > 0 and not urls:
            problems.append(f"{tag} scores {score} with no source URL")
        if score == 0 and tag not in unverified:
            problems.append(f"{tag} scores 0 but is not marked unverified")
    # Unscored text columns state facts too (names, systems), so they need sources.
    for col in TEXT_FACTS:
        if row.get(col, "").strip() and not sources.get(col):
            problems.append(f"{col} is filled in with no source URL")
    return problems


def rank(rows, weights=WEIGHTS):
    """Attach score_trigger and total_score, and return rows sorted best first.

    Ties break on deal flow, then on firm name, so the order never depends on
    the order of rows in the CSV.
    """
    for row in rows:
        row["score_trigger"] = str(trigger_score(row))
        scores = {d: int(row[f"score_{d}"]) for d in weights}
        row["total_score"] = f"{weighted_total(scores, weights):.1f}"
    return sorted(
        rows,
        key=lambda r: (-float(r["total_score"]), -int(r["score_deal_flow"]), r["firm"]),
    )


def main():
    assert sum(WEIGHTS.values()) == 100, "weights must sum to 100"

    with open(TARGETS_CSV, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        fields = reader.fieldnames
        rows = list(reader)

    errors = {r["firm"]: check_row(r) for r in rows}
    errors = {firm: p for firm, p in errors.items() if p}
    if errors:
        for firm, problems in errors.items():
            print(f"{firm}: " + "; ".join(problems))
        raise SystemExit("Evidence rule broken. Fix the CSV before ranking.")

    ranked = rank(rows)

    # Write the totals back so the CSV is complete on its own, then a ranked copy.
    with open(TARGETS_CSV, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(ranked)

    os.makedirs(os.path.dirname(RANKED_CSV), exist_ok=True)
    with open(RANKED_CSV, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["rank"] + fields)
        writer.writeheader()
        for i, row in enumerate(ranked, start=1):
            writer.writerow({"rank": i, **row})

    print(f"Ranked {len(ranked)} firms -> {RANKED_CSV}\n")
    for i, row in enumerate(ranked, start=1):
        print(f"{i:>2}  {row['total_score']:>5}  {row['firm']}")


if __name__ == "__main__":
    main()
