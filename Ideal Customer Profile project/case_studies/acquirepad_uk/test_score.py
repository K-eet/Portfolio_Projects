"""Tests for score.py, each named for the rule it protects."""

import score

DIRECT = [d for d in score.WEIGHTS if d != "trigger"]
ALL_TAGS = DIRECT + [tag for tag, _ in score.TRIGGER_PARTS.values()]


def make_row(firm="Firm", sources="", unverified=None, event=0, active=0, data=0, **scores):
    row = {"firm": firm, "sources": sources,
           "trigger_event": str(event), "trigger_active_capital": str(active),
           "trigger_data_hire": str(data)}
    for dim in DIRECT:
        row[f"score_{dim}"] = str(scores.get(dim, 0))
    if unverified is None:
        zero = [d for d in DIRECT if not scores.get(d)]
        zero += [t for t, v in (("trigger_event", event), ("active_capital", active),
                                ("data_hire", data)) if not v]
        unverified = ";".join(zero)
    row["unverified"] = unverified
    return row


def test_weights_sum_to_100_so_totals_need_no_rescaling():
    assert sum(score.WEIGHTS.values()) == 100


def test_full_marks_on_every_dimension_scores_100():
    assert score.weighted_total({d: 3 for d in score.WEIGHTS}) == 100


def test_trigger_parts_add_up_and_cap_at_three():
    assert score.trigger_score(make_row(event=2, active=1)) == 3
    assert score.trigger_score(make_row(event=2, active=1, data=1)) == 3
    assert score.trigger_score(make_row(active=1)) == 1


def test_a_score_above_zero_without_a_url_is_rejected():
    row = make_row(deal_flow=2)
    assert any("deal_flow" in p for p in score.check_row(row))


def test_active_capital_needs_its_own_source():
    row = make_row(active=1, sources="trigger_event: https://example.com/a")
    assert any("active_capital" in p for p in score.check_row(row))


def test_a_zero_score_must_be_marked_unverified():
    row = make_row(unverified="segment")
    assert any("warm_path" in p for p in score.check_row(row))


def test_a_fully_sourced_row_passes():
    row = make_row(deal_flow=3, active=1,
                   sources="deal_flow: https://example.com/a | active_capital: https://example.com/b")
    assert score.check_row(row) == []


def test_a_named_first_move_needs_a_source():
    row = make_row()
    row["first_move"] = "Jane Doe, head of acquisitions."
    assert any("first_move" in p for p in score.check_row(row))


def test_ties_break_on_deal_flow_not_on_csv_order():
    busy = make_row("Busy", deal_flow=3)
    quiet = make_row("Quiet", segment=3)
    weights = {d: 0 for d in score.WEIGHTS} | {"deal_flow": 50, "segment": 50}
    ranked = score.rank([quiet, busy], weights)
    assert [r["firm"] for r in ranked] == ["Busy", "Quiet"]
