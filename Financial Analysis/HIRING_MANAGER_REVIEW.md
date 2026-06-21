# Hiring Manager Review & Roadmap

> **Purpose of this file.** This is a standing reference for future Claude Code
> instances working on this project. It captures a buy-side hiring manager's
> assessment of the portfolio, what has already been addressed, and the prioritized
> next steps. Read this before making changes so you build on the existing direction
> rather than re-deriving it. Update the "Status" markers as items get done.

**Roleplay frame:** The reviewer is a hiring manager at a buy-side firm (fundamental
long/short equity) evaluating this repo as a fresh-grad candidate's portfolio. The bar
is not "can this person code" — it's "does this person think like an investor."

---

## The One Thing That Matters

Buy-side does not pay for dashboards. It pays for **a defensible, valuation-backed
view** — a thesis, a catalyst, a risk that would falsify it. Every change to this repo
should push it further toward *"thinks like an analyst"* and away from *"plots financial
data."* When in doubt, ask: *does this help the reader form or stress-test an
investment view?* If not, it's secondary.

---

## Candidate Strengths (preserve these — don't refactor them away)

- **Interprets, doesn't just plot.** The narrative cells contain real insight, not chart
  captions. The standout: Ford converts earnings to cash *better than Tesla* despite
  lower margins (notebook 03). Keep this analytical voice.
- **Earnings-quality instinct.** Reaching for Cash Conversion Ratio (OCF / Net Income)
  is above-median for a fresh grad — signals thinking about *quality* of earnings.
- **Intellectual honesty.** The data-limitations disclosures (yfinance history cap,
  fiscal-year assumption) are exactly the disclosure discipline buy-side wants.
- **Comparative, archetype-based framing.** Three EV archetypes (pure-play / volume /
  legacy) rather than one ticker — investors think in relative terms.
- **Structured thesis.** Notebook 04 applies the SCIR framework (Situation,
  Complication, Implication, Risk) with a variant-perception angle. This is the single
  biggest leap from "student project" to "analyst work."

## Weaknesses (the work queue)

| # | Weakness | Status |
|---|----------|--------|
| 1 | Was a dashboard, not a thesis — no investment view | ✅ Addressed (notebook 04, SCIR + ranking) |
| 2 | No valuation layer — couldn't connect fundamentals to price | ✅ Addressed (notebook 05: P/E, FCF yield, EV/EBITDA) |
| 3 | `current_year` used-before-defined bug in deep dive | ✅ Fixed by candidate |
| 4 | Notebook naming mismatch (02 was "data_cleaning", actually viz) | ✅ Fixed (renamed `02_visualization.ipynb`) |
| 5 | README undersold the work; said "work in progress" | ✅ Fixed (full rewrite) |
| 6 | **Thin dataset — 3 annual data points per company** | ⬜ Open |
| 7 | **No quarterly granularity** — trend claims rest on 2 YoY deltas | ⬜ Open |
| 8 | **Metric logic lives in notebook cells**, depends on hidden kernel state | ⬜ Open |
| 9 | **No tests** — nothing guards the metric calculations | ⬜ Open |
| 10 | Segment-level analysis missing (Ford ICE vs EV, Tesla auto vs energy/credits) | ⬜ Open |
| 11 | Valuation is point-in-time multiples only — no reverse-DCF / "what's priced in" | ⬜ Open |
| 12 | Pickle files as the data interface — opaque, not diff-able, can go stale | ⬜ Consider |

---

## Prioritized Next Steps

These are ordered by **return on effort for a buy-side application.** Do the top items
first; they move the needle most.

### P1 — Deepen the analytical edge (highest impact)
1. **Reverse-DCF on Tesla.** "What FCF growth rate does the ~188x P/E imply, and is it
   achievable?" This is the most analyst-like artifact the repo could add. Connects the
   valuation gap (notebook 05) directly to a falsifiable claim.
2. **Segment breakout.** Tesla's regulatory-credit revenue and Ford Blue/Pro vs Model e.
   The aggregate numbers hide the real story; segment data is where differentiated
   insight lives. Pull from 10-K/10-Q segment notes (EDGAR).
3. **Extend history + go quarterly** via SEC EDGAR (free, full history, XBRL). Fixes
   weaknesses #6 and #7 at once and demonstrates the candidate can handle filings, not
   just a convenience API. This is the single biggest data-quality upgrade.

### P2 — Demonstrate engineering rigor
4. **Extract metric logic into a tested module.** Move NPM / ROA / FCF / CCR / valuation
   math out of notebook cells into e.g. `src/metrics.py`, import it into the notebooks.
   Add `pytest` cases with known inputs/outputs. Directly answers the "doesn't depend on
   hidden kernel state" concern (the original `current_year` bug was exactly this class
   of problem).
5. **Make notebooks runnable top-to-bottom from a clean kernel.** Restart-and-run-all
   should produce every output with no `NameError`s or cross-notebook leakage. Verify
   before claiming done.

### P3 — Polish & presentation
6. **Export the dashboards** (notebook 02/05 Plotly figures) to static PNG/HTML so a
   reviewer sees results without running anything. Embed key charts in the README.
7. **Lead the README with the conclusion** — it already does; keep it that way. The
   188x-vs-2.4x headline is the hook.
8. **Add a one-paragraph "What would change my mind"** per company. Buy-side respects a
   pre-committed falsification condition; the SCIR "Risk" sections are the seed for this.

---

## Project Map (orientation for new instances)

Pipeline — each notebook consumes the previous one's pickle output. **Notebook 01 must
run first** (produces `data/metrics.pkl` and `data/raw_data.pkl`).

| Notebook | Role |
|----------|------|
| `notebooks/01_data_collection.ipynb` | Pull statements from yfinance, compute core metrics, clean partial/NaN years, persist to pickle |
| `notebooks/02_visualization.ipynb` | Plotly dashboard: NPM, FCF, ROA |
| `notebooks/03_deep_dive.ipynb` | YoY change + Cash Conversion Ratio (earnings quality) |
| `notebooks/04_investment_thesis.ipynb` | SCIR thesis per company + comparative ranking |
| `notebooks/05_valuation.ipynb` | P/E, FCF yield, EV/EBITDA from year-end market caps |

**Companies:** Tesla (TSLA, pure-play EV), BYD (BYDDY ADR, volume), Ford (F, legacy).
**Coverage:** 2022–2024 annual (yfinance free-tier limit after dropping partial/NaN years).

### Known data facts (as computed, 2024)
- NPM: Tesla 7.3% · BYD 5.2% · Ford 3.2%
- ROA: Tesla 5.8% · BYD 5.1% · Ford 2.1%
- FCF: Tesla ~$3.6B · BYD ~$36.1B · Ford ~$6.7B
- CCR: Tesla 2.09 · BYD 3.32 · Ford 2.62
- Headline valuation gap: Tesla ~188x P/E vs BYD ~2.4x — driven by growth expectations
  and geopolitical risk premium, not current fundamentals.

> Verify these against a fresh run before quoting them as fact in new work — they were
> read from notebook outputs, not independently recomputed.

---

## Conventions & Gotchas

- **Remote uses SSH** (`git@github.com:K-eet/Portfolio_Projects.git`). HTTPS push fails
  on this headless server (no `gh`, no credential helper); SSH key `id_ed25519`
  authenticates as K-eet. Don't switch the remote back to HTTPS.
- **`.pkl` files** are the inter-notebook data interface. They're gitignored by pattern
  but currently present in `data/`. If metric logic changes, regenerate them by
  re-running notebook 01 — stale pickles will silently feed old numbers downstream.
- **Consistent company colors** across notebooks: Tesla `#E31937`, BYD `#1DB954`,
  Ford `#003DA5`. Keep these for visual continuity.
- **Author:** Lee Keet Men. Keep author attribution on notebooks where present.

---

## Bottom-Line Verdict (current state)

Worth a phone screen, and materially stronger than when first reviewed. The candidate
closed the two biggest gaps — there is now an investment thesis *and* a valuation that
ties fundamentals to price. To move from "interesting maybe" to "bring them in," the
remaining edge is **depth over breadth**: a reverse-DCF, segment-level analysis, and
quarterly data on these *same three companies* would do more than adding a fourth ticker
or another chart. Rigor (tested metric module, clean-kernel reproducibility) is the
secondary signal that says "won't blow up on a bad number."
