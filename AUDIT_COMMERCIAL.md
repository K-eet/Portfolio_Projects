# Portfolio Audit — Re-run for Commercial Roles

**Repo:** `github.com/K-eet/Portfolio_Projects` · **Re-audited:** 8 August 2026
**Supersedes:** `AUDIT.md` (written for analyst roles — kept, not deleted, because the factual
inventory in §1 there is still accurate and you may have already acted on parts of it).
**Scope:** audit only. No files edited or created except this one.
**Progress:** see **§0.1** (e-commerce/churn) and **§0.2** (Financial Analysis) — both closed
6 September 2026.

Three target tracks:
- **Track 1 — Pure Outbound.** SDR / BDR / Inside Sales / Commercial Development Rep.
- **Track 2 — Founder in Training.** Founder's Associate / Founding SDR / Growth Associate / Chief of Staff Associate.
- **Track 3 — Technical Commercial.** Associate or Graduate Solutions Engineer / Pre-Sales Engineer / Technical Sales / Commercial Engineer.

---

## 0. The headline, before the detail

**The repository matters far less than it did, and differently per track.** For analyst roles the
repo *was* the artefact. For these three, the artefact is your email, your CV and how you perform
in a call. The repo is supporting evidence — and for one of these tracks it is barely evidence at
all.

| | Weight in the hiring decision | Does the manager open GitHub? |
|---|---|---|
| **Track 1 — SDR/BDR** | **~10–15%** | Rarely. Screening is CV → phone screen → role-play. |
| **Track 2 — Founder's Associate** | **~40%** | Yes. Founders click links and form fast judgements. |
| **Track 3 — Solutions Engineer** | **~50%** | Yes, and they read the code. Best fit for current contents. |

**Five reversals from the previous audit.** These are direct contradictions of what I told you
last time, and the change of audience is why:

| Item | Previous verdict | New verdict |
|---|---|---|
| Berkshire new-build premium | **Top priority, build it first** | **Demoted.** Demonstrates property analysis, not commercial ability. Build only if targeting proptech. |
| Churn steps 3–4 | **Don't finish. Leave in progress.** | **Finish it — high priority.** Pricing errors against a naive rule *is* an ROI business case, which is core Solutions Engineer and Founder's Associate work. |
| SCIR investment thesis | "Keep, good writing" | **Your single most valuable asset for Tracks 2 and 3** — and it needs an editing pass it hasn't had. |
| `Customer_Segmentation` | Cut (confidentiality) | **Still cut the folder** — but its *concept* is now the model for your best new project. See §4. |
| BYD currency error | Fix first, credibility | **Fix first, harder.** In commercial roles, misstating a number by 7× in front of a buyer isn't embarrassing, it's disqualifying. ⟶ **DONE 6 Sep — and it moved the conclusions, not just the figures. See §0.2.** |

**What doesn't change:** delete `Customer_Segmentation` (a published customer ledger with credit
terms is a liability under any job title), delete the 2-byte `.pbix`, delete the orphan SQL file,
commit the two untracked churn notebooks, fix the root README's "two projects" over three folders.
Those cost about two hours and remain the highest-leverage two hours available.

> **Status, 6 Sep 2026:** all of these are done except the root README, which the owner is holding
> until all three projects are finished. See **§0.1** and **§0.2** for the full progress logs.

---

## 0.1 Progress log — 6 September 2026

*Added after the audit was written. Covers the **e-commerce / churn project only**. Financial
Analysis is being worked separately and nothing below reports on it.*

| Audit item | Raised in | Status |
|---|---|---|
| Churn steps 3–4 — the ROI case | §3, §6.2 (hours 12–15) | **Done.** `6. cost_and_benchmark.ipynb`, committed `96ce60d` |
| Notebooks 1 & 2 blank | §3, §6.3 | **Done.** All six notebooks now run top to bottom against one regenerated dataset, no errors |
| E-commerce README stale figures | §3 | **Done.** See the correction below — one figure was right, two were invented |
| Commit the churn notebooks | §0, §6.1 item 3 | **Done.** 4 and 5 committed earlier; 6 committed with this work |
| Delete `Customer_Segmentation/`, `.pbix`, orphan SQL | §0, §6.1 items 1–2 | **Done** in an earlier commit; verified absent from the working tree and from `git ls-files` |

### The churn result — §7's missing line 2 is now writable

> With an unlimited contact budget the model is worth **£0.23 per customer** over a *tuned* silence
> rule — nothing. Under a budget of 100 contacts, ranking by predicted probability **×** value at
> risk returns a median **£7,132** against **£4,022** for the rule, while ranking by probability
> alone does worse than choosing at random.

The audit predicted the useful finding would be "the money gap between model and rule", and allowed
that the gap might favour the rule. It does — £136 across 587 customers, surviving no combination of
contact cost and save rate tested. What the audit did not anticipate is the second half: the gap
only appears under a **contact budget**, and only once probabilities are multiplied by customer
value. For a commercial reader that is the sharper sentence — *the classifier isn't the product,
the prioritised call list is* — and it is a better answer than the marginal win §6.2 hoped for.

Note also what the rule was benchmarked at. Against the 90-day rule **as originally written down**,
the model appears to win by £13,690. That number is real and would have been easy to report. It is
not a win for the model; it is a win for contacting more people, which the rule does just as well
once its own threshold is swept. Sweeping both sides is what turns a £13,690 illusion into a £136
fact.

### On the stale README figures — the audit was half right

**399,689 is correct.** It was unverifiable only because notebooks 1 and 2 had never been run; the
chain now reproduces it exactly (541,909 → −135,080 null CustomerID → −5,225 duplicates → −1,915
invalid StockCodes). **41.3% and 42.5% were invented** — no such figures exist anywhere in the
analysis. The real segmentation is Champions 40.7% / At Risk 40.7% / Big Spenders 9.3% / Loyal 9.3%,
and it carries a better line than the one it replaced: the 40.7% Champions produce **83.6%** of
revenue while the equally sized At Risk group produce **5.8%**.

### Two defects this audit did not catch, both in `3. EDA.ipynb`

1. **Currency.** The project's headline retention number printed as `$416.35` / `$2,866.96` on a UK
   retailer's GBP data — 8 occurrences across 5 cells. This is the same defect class §0 calls
   *disqualifying*, sitting inside the one number §7 lists as verified. Now GBP throughout.
2. **Double-counted products.** The Pareto analysis grouped by `(StockCode, Description)`, so any
   product whose description varies between transactions counted more than once — 3,891 groups
   against 3,659 real StockCodes, contradicting the same notebook's own header four cells earlier.
   That count is the *denominator* of the headline, so **§7's drafted e-commerce line is wrong:
   21.4% of products drive 80% of revenue, not 21%.** Fixed in the notebook, with an assertion
   pinning the row count to `df['StockCode'].nunique()`, and corrected in the README.

### Still open, unchanged by this work

`git mv` to `ecommerce-analytics` (§6.1 item 4) · the root README rewrite (§6.1 item 5, §7) —
deferred by the owner until all three projects are finished · the ICP project (§4) · the deployed
artefact and the Loom (§6.3) · everything in Financial Analysis — **now closed, see §0.2**.

---

## 0.2 Progress log — Financial Analysis, 6 September 2026

*Added after §0.1. Covers the **Financial Analysis project only**. Committed as
`4fce548` on branch `fix/financial-analysis-currency-and-scope`.*

| Audit item | Raised in | Status |
|---|---|---|
| BYD CNY/USD currency error | §0, §1, §3, §6.1 item 6, §6.2 | **Done.** Diagnosis confirmed empirically — `BYDDY.info` returns `financialCurrency=CNY` with `currency=USD` |
| Tesla's P/E — three figures, one company | §1, §6.2 | **Done.** One figure everywhere: **189.3×**. See the note below on why it is not 188× |
| "NPM dropped by 8.2% and its ROA dropped by 8.2%" | §1, §6.2 | **Done.** −8.2pp and −9.4pp respectively, and both now stated as *points* |
| "Its CCR is 2.09, barely above 1" | §1, §6.2 | **Done.** 2.10, described as the lowest of the three but still double 1 |
| Ranking contradicts the rest of the repo | §1, §6.2 | **Done.** BYD → Ford → Tesla, identical in notebooks 04 and 05 and the README |
| SCIR prose — proofread and reconcile | §3, §6.2 (hours 4–5) | **Done.** Rewritten rather than proofread — see below |
| `edgar_utils.py` — "archive in place, don't extend" | §3 | **Deliberately not followed.** The owner directed EDGAR to become the *primary* source. See the deviation note |
| `02_visualization.ipynb` (3 cells) — CUT as padding | §3 | **Not done.** The owner declined the merge into 03. It now carries a snapshot table and an interpretation, so it is no longer three cells of padding, but it is still a thin notebook |
| Export the Plotly charts to PNG | §6.3 | **Still open.** The six charts render only in a live kernel |

### The currency fix changed the conclusion, not just the figures

The audit treated this as a credibility defect — a right answer stated wrongly. It is not. Once
BYD's renminbi statements are translated, **the analysis reaches different conclusions**:

| 2024 | Before | After |
|---|---:|---:|
| BYD free cash flow | $36.1B | **$5.02B** |
| BYD P/E | 2.4× | **17.5×** |
| BYD FCF yield | 36.8% | **5.1%** |

The consequential one is not BYD's own numbers but the ranking they implied. In a single currency,
**Ford is the largest absolute cash generator of the three** — $6.74B against BYD's $5.02B and
Tesla's $3.58B — so BYD is no longer cheapest on every metric, and the claim the old README led
with was wrong in *direction* as well as magnitude. Ford's thesis was upgraded and BYD's
downgraded on the strength of it. The notebooks say so explicitly rather than quietly restating
the numbers.

Ford also produced the finding the corrected data made visible: it is cheapest on P/E (6.0×) and
FCF yield (19.1%) yet mid-pack on EV/EBITDA (12.2× against BYD's 5.5×), because it carries
**$160.9B of debt against a $35.2B market cap** — 4.6×, almost all of it Ford Credit. Two lenses
disagreeing about the same company is a better paragraph than anything in the original version.

### On §7's drafted line — the audit was half right, again

§7 drafted: *"The market pays ~188× earnings for Tesla against ~18× for BYD, despite BYD generating
more free cash flow and converting earnings to cash more reliably."*

- **~18× for BYD was a good estimate** — the true figure is 17.5×.
- **~188× was not quite right, for an interesting reason.** 188.3 was yfinance's figure. Against
  as-filed EDGAR net income the multiple is **189.3×**. The audit could not have known this, but it
  means the "one figure" the repo reconciles to is not the one §7 predicted.
- **"BYD generating more free cash flow" needs a qualifier.** More than Tesla, yes. Not more than
  Ford. Written as drafted it would have reproduced the original error in gentler language.
- **"converting earnings to cash more reliably" holds** — BYD's cash conversion of 3.32 is the
  highest of the three.

### Four defects this audit did not catch

1. **The analysis window was on a timer.** Notebooks 01, 03 and 04 derived their cutoff from
   `datetime.today().year - 2`, while notebook 05 hard-coded 2024. It happens to resolve to
   2022–2024 today. In January 2027 it would have silently become 2023–2025 while every sentence of
   the prose stayed pinned to the old years — the stale-figures defect §0.1 found in e-commerce,
   except scheduled rather than committed. Replaced with one `config.ANALYSIS_YEARS` constant.
2. **The documented run order crashed.** Notebook 04 argued from valuation multiples that notebook
   05 wrote to disk, so the README's own "run 01 → 05 in order" instruction failed on a clean
   checkout. Price collection moved into notebook 01. This is the §0.1 defect class again: an
   instruction nobody had executed end to end.
3. **`quarterly_edgar.pkl` was consumed by nothing.** Notebook 01 spent 200 lines and a validation
   suite building a quarterly dataset no downstream notebook read, and the README did not mention
   the phase existed. Now a labelled appendix that states it is not part of the pipeline.
4. **The setup instructions did not work.** `requirements.txt` contained no Jupyter package despite
   the README's `jupyter lab` instruction, and `.venv/` was not in `.gitignore`.

### The deviation from §3 — EDGAR, "don't extend it"

§3 said to archive `edgar_utils.py` in place and stop investing. The owner directed the opposite:
EDGAR is now the **primary** source for Tesla and Ford, on as-filed 10-K figures rather than vendor
aggregates.

It could not become the source for everything, and the reason is worth recording because it is a
limitation to state rather than a gap to apologise for. **BYD files nothing financial with the
SEC.** Its only EDGAR presence, CIK 1445162, is ADR registration paperwork — `F-6EF`, `F-6 POS`,
`424B3` — filed by the depositary bank; there is no 20-F, no 10-K, and `companyfacts` returns
**404**. EBITDA, total debt and share count also stayed on yfinance for all three companies,
because Ford and Tesla tag them incompatibly in XBRL and sourcing them per filer would have
quietly rebuilt the same apples-to-oranges comparison the currency fix had just removed.

Against §3's commercial-legibility argument this is a real cost: it is more engineering in the
project, not less. Against Track 3 it is the opposite — a candidate who can say *why* a data source
cannot answer a question is doing the pre-sales job §2 describes.

### What now guards the fix

- `fx.py` requires an explicit `flow` or `stock` argument with **no default**, because choosing
  silently is the error itself.
- `test_fx.py` pins the regression: CNY 36.094B must translate to ~$5.0B. 24 tests pass.
- Notebook 01 asserts a cross-company revenue-spread check. Verified as more than decorative by
  re-introducing the original bug against real data: 1.89× corrected, **8.0× and failing** when BYD
  is left in renminbi.
- All 41 figures quoted in the README and notebooks were cross-checked against the pipeline output.

**One residual, disclosed rather than fixed.** BYD's ROA reads 5.22% translated against 5.14% as
reported in renminbi, because net income translates at the average rate and total assets at the
year-end rate. That is standard practice, but it means BYD's ROA is not strictly like-for-like with
Tesla's and Ford's, and the README says so.

### Still open in Financial Analysis

Exporting the six Plotly charts to PNG (§6.3) · folding `02_visualization.ipynb` into 03 (§3 —
declined) · the "So what would you do about it?" section §7 asks for on every project.

---

## 1. Inventory — what changed in the reading

The file inventory in `AUDIT.md` §1 is unchanged and still accurate. What changes is which files
matter. Re-sorted by value to these three tracks:

| Asset | Old rank | New rank | Why |
|---|---|---|---|
| `04_investment_thesis.ipynb` — SCIR prose | Mid | **1st** | Structured persuasive writing. This is the skeleton of a discovery call and an outbound email. |
| Churn notebooks 4, 5 & 6 (**now committed**) | 2nd | **2nd** | A retention/revenue question with an explicit cost framing. Commercially legible. |
| `03_deep_dive.ipynb` earnings-quality reasoning | Mid | **3rd** | Shows you interrogate a number rather than report it. |
| `edgar_utils.py` + tests | **1st** (best engineering) | **4th** | Real engineering, but no buyer, founder or sales manager will ever read it. Keep; stop investing. |
| `3. EDA.ipynb` | Mid | Mid | Only e-commerce notebook with visible charts. Source of your one usable number. |
| Berkshire project (unbuilt) | **1st priority** | Conditional | Only if you target proptech. See §5. |
| `sql_queries_eda.sql`, `.pbix`, `Customer_Segmentation/` | Cut | Cut | Unchanged. |

**One new defect class, invisible under the old lens.** I read the SCIR markdown properly this
time. The *thinking* is good. The *execution* has errors that were minor for an analyst audience
and are serious for these three, because in all three tracks your writing is the product:

- **Tesla's P/E appears as three different numbers in three places.** Notebook 04 says
  *"it trades at ~50x earnings vs Ford's ~6x"*. Notebook 05's executed output says **188.3**. The
  README says **188x**. The 50x figure is Tesla's *2023* multiple used in a 2024 argument. A
  reader who checks two files finds the repo contradicting itself on its own headline metric.
- **A stated figure is simply wrong.** *"NPM dropped by 8.2% and its ROA dropped by 8.2%"* — from
  your own outputs, NPM fell 15.4→7.3 (8.1pp) but ROA fell 15.3→5.8, which is **9.4pp**, not 8.2.
  Both are also percentage-*point* moves described as percentages.
- **A characterisation that contradicts the number next to it.** *"Its CCR is 2.09, barely above
  1"* — 2.09 is more than double 1. The sentence argues the opposite of the figure it cites.
- **The ranking contradicts the rest of the repo.** Notebook 04 ranks **Tesla 1st**; notebook 05's
  scorecard and the README's narrative both say BYD. You have a written justification for the
  Tesla ranking, so this is a defensible position — but it is never reconciled with the README,
  which reads as the project disagreeing with itself.
- **Uncorrected typos in the showcase document:** "THe FCF decline", "tesla" mid-sentence, "its
  trying to compete" for "it's", doubled spaces.

Set against that, the reasoning is genuinely strong. *"Ford is funding an EV transition using
profits from the business the transition is killing"* is a sentence that would land in a real
commercial conversation. The variant-perception sections do the hardest thing in analysis — state
what the market believes, then say why it's wrong and what would prove you wrong. **The strategy
is there and the proofreading isn't**, which for an outbound role is exactly the wrong way round.

> **Status, 6 Sep 2026.** Every defect in the five bullets above is closed (**§0.2**). The bullets
> are left in the present tense as the original finding. Two corrections to them, for the record:
> the reconciled P/E is **189.3×**, not the 188.3 quoted here — 188.3 was yfinance's figure and the
> repo now runs on as-filed EDGAR data — and the NPM fall is **8.2pp**, not the 8.1 stated above,
> for the same reason. The 9.4pp ROA figure was right. It also turned out that "the proofreading
> isn't" understated the problem: the BYD and Ford theses were not mis-proofread but mis-argued,
> because they rested on the uncorrected currency figures, and both had to be rewritten.

---

## 2. What each hiring manager sees

### Track 1 — SDR / BDR

**Most will never open the link.** SDR screening is CV, then a phone screen for energy and
coachability, then a role-play. Assume the repo is read by roughly one manager in five, for under
a minute.

For the one who does look, the risk is not that the work is bad. It's **intent**. He sees SEC XBRL
extraction pipelines, pytest suites, logistic regression with leakage assertions, and an
investment thesis — and concludes: *this person wants to be a data analyst and is applying to SDR
roles as a stopgap.* SDR managers are acutely sensitive to this. Ramp is about three months and
median tenure is short; a hire who leaves at month seven for an analyst job is a straight loss.
Technical depth with no commercial framing reads as flight risk.

The current README makes this worse by opening with *"This repository contains two end-to-end data
analytics projects…"* and naming a **Business Intelligence Analyst application** in sentence two.
That is the flight-risk hypothesis, confirmed in writing, on the landing page.

What he *would* value, and cannot currently find: evidence you can research an account, build and
prioritise a list, and write. Nothing in the repo speaks to any of that.

**Conclusion:** currently mildly negative. Not because it's broken — because it argues for a
different job.

### Track 2 — Founder's Associate / Founding SDR / Growth Associate

**This reader definitely opens it,** and this is the track where the repo's actual state hurts
most.

The role is defined by agency: given a vague problem and no supervision, do you close the loop?
The founder is reading the repo as a behavioural sample, not a skills test.

What the sample shows: three projects, one advertising a dashboard file that 404s, three notebooks
with no outputs, six charts that render blank, README figures that contradict the notebooks
beneath them, a headline number wrong by ~7×, and a directory containing a third party's customer
ledger. The two best notebooks aren't committed at all.

He does not conclude "can't do the work." He concludes **"starts things."** For a Founder's
Associate that is close to the only disqualifying trait, because the job is being handed the
things nobody else has time to finish.

> **Status, 6 Sep 2026.** That paragraph is the assessment as written on 8 August; it is left
> standing rather than edited, because the point of it is what a founder saw on that date. Of the
> seven defects it lists, five are now cleared: the 404ing dashboard file and the customer ledger
> are deleted, the two blank e-commerce notebooks run, the e-commerce README no longer contradicts
> its notebooks, and the best notebooks are committed. Two remain, both in Financial Analysis: the
> six blank Plotly charts and the headline number wrong by ~7×. **The specific charge — "starts
> things" — is the one this work was aimed at**, and it is answered by finishing the churn
> sequence rather than by any single fix in it.

The material underneath would genuinely impress this reader — breadth from equities to retail
churn to SEC filings, self-taught, with a structured commercial framework applied on top. He can't
see it in ninety seconds, and the surface tells him not to look.

**Conclusion:** currently negative, on the one dimension the role selects for.

### Track 3 — Solutions Engineer / Pre-Sales / Technical Sales

**Best fit for what actually exists, and the reader most likely to read carefully.**

A pre-sales manager is hiring for: technical credibility with a CTO, and the ability to explain
something technical to someone who won't read the detail. He'll find real evidence of the first.
The EDGAR pipeline handling YTD-versus-discrete flows and tag migrations is unusual for a
graduate. The churn notebooks' leakage assertions show you know how analyses fail.

More valuable than either: **your limitations sections**. "yfinance caps history at ~4 years",
"the two observation windows differ so the AUCs aren't like-for-like", "this is the one assumption
that, if wrong, breaks the conclusion". Being precise about what your thing *cannot* do is a
core pre-sales skill — it's how you handle an objection without losing the room. Most graduate
candidates have no instinct for it. You have a documented one.

Three things work against you:

1. **The numeric contradictions in §1 are fatal in this specific role.** A Solutions Engineer's
   entire value is being the person in the room whose numbers are right. Three different P/E
   figures for the same company, and a headline off by 7×, is the exact failure mode this job
   exists to prevent.
2. **Notebooks are the wrong format.** Nobody in a commercial cycle reads a notebook. This role's
   native artefacts are a demo, a one-pager, a business case. You have none.
3. **No evidence of explaining to a non-technical audience.** Everything here is written for
   someone who already understands the domain.

**Conclusion:** currently neutral-to-slightly-positive — the only track where the repo helps
today. With the §6 fixes it becomes a genuine advantage.

---

## 3. Scope creep and dead weight, re-scored

| Item | Verdict | Reason under the new lens |
|---|---|---|
| `Customer_Segmentation/` | **CUT** (unchanged) | Liability is title-independent. Purge from history — `AUDIT.md` §8 has the commands. |
| `.pbix` (2 B), `sql_queries_eda.sql` | **CUT** (unchanged) | Advertising things that don't exist is worse for sales roles, where overstating is the cardinal sin. |
| `02_visualization.ipynb` (3 cells) | **DECLINED** (6 Sep) | Padding. Owner kept it; now carries a snapshot table and interpretation, but still thin. |
| **Numeric contradictions across Financial Analysis** | **DONE** (6 Sep) ⟵ *was: FIX FIRST* | Was #1 by credibility. Correcting it changed the ranking and the headline finding — see §0.2. |
| **SCIR prose — proofread and reconcile** | **DONE** (6 Sep) | Rewritten, not proofread: the corrected data invalidated the BYD and Ford theses. See §0.2. |
| Churn steps 3–4 | **DONE** (6 Sep) ⟵ *was: FINISH, reversed* | An ROI case with a do-nothing benchmark. Directly transferable to a business case. |
| Berkshire new-build premium | **CONDITIONAL** ⟵ *demoted* | Only if targeting proptech/contech. |
| `edgar_utils.py` + EDGAR pipeline | **OVERRULED** (6 Sep) ⟵ *was: ARCHIVE in place* | Owner made EDGAR the primary source for Tesla and Ford. Deviation and its cost recorded in §0.2. |
| Notebooks 1 & 2 blank | **DONE** (6 Sep) | Cheap, and it turned 399,689 from an assertion into a reproducible figure. |
| E-commerce README stale figures | **DONE** (6 Sep) | 399,689 verified once the notebooks were run; 41.3% / 42.5% did not exist and were replaced. See §0.1. |
| Root README | **REWRITE — commercially** | See §7. The current framing actively argues for a different job. |
| **A deployed, clickable artefact** | **ADD — new** | Essential for Track 3, valuable for Track 2, harmless for Track 1. |
| **A commercially-framed project** | **ADD — new, highest value** | See §4. The single biggest gap for all three tracks. |

---

## 4. The gap that replaces the built-environment gap

The previous audit's central finding was that the repo said nothing to construction employers.
Under these three tracks the central finding is different:

**Nothing in this repo demonstrates commercial thinking applied to a commercial problem.** Every
project analyses a business from the outside — a retailer's customers, a carmaker's filings. None
of them does the thing all three roles require: *identify who to go after, and why them first.*

The irony is that the one project I told you to delete is the closest. `Customer_Segmentation`
asked "which 100 customers should we target for a campaign, and in what order?" — that is
prioritised target-account selection, which is literally the SDR's daily job and the Founder's
Associate's first assignment. **The folder must still go** (the data liability is unchanged), but
the *question* is the right one. Rebuild it on public data.

### Recommended new centrepiece — an ICP and target-account model

**Business question:** Which UK companies should [a given B2B product] approach first, and what
makes them a better prospect than the ones ranked below?

**Data:** the **Companies House Free Company Data Product** — a free monthly CSV snapshot of
roughly 5 million UK companies, including company number, registered address, status,
incorporation date and **SIC code**, with no API key required. ZIP is ~400 MB, uncompressed ~2 GB,
and it's also published in smaller partitions. *(High confidence — this is an official Companies
House product; see sources at the end.)* Filter by SIC code, region and incorporation date to
define a segment, then score and rank.

**Deliverable:** a README with the scoring logic in five lines, a ranked table of the top 25
accounts, one chart of the segment, and — critically — **three example outbound emails written to
the top three accounts**, each citing a specific fact from the data about that company.

**Why this single project serves all three tracks:**

- **Track 1:** it *is* the job. An SDR candidate who arrives having already built and prioritised
  a target list, with three written emails to prove it, is doing the role before being hired. It
  also destroys the flight-risk objection — this is not an analyst's portfolio piece.
- **Track 2:** it demonstrates commercial agency. Picking a segment, defending the choice, and
  producing something actionable is exactly the first task a founder hands over.
- **Track 3:** it shows you can turn data into a commercial argument and write for a buyer, which
  is the half of Solutions Engineering the rest of the repo doesn't evidence.

**Hours: 6–8.** The data is a straightforward CSV filter; the scoring is a weighted rank, not a
model. Resist making it a model — the value is in the reasoning and the emails, not the maths.
Deliberately keep it simple, and say in the README that you kept it simple because a transparent
score a sales team will actually trust beats an opaque one they won't.

### On the built-environment angle — keep it, as targeting

You haven't said whether you've dropped the construction positioning. **My recommendation: keep it,
but change what it's for.** It's no longer the subject of your portfolio; it's your *choice of
employer*.

Apply to **construction tech and proptech companies** in these roles. The logic holds across all
three tracks: those companies sell to quantity surveyors, contractors and developers, and their
single hardest hiring problem is finding commercial staff who can hold a credible conversation
with that buyer. A civil engineering graduate who can talk to a QS without a script is worth
markedly more to them than a generic SDR — and unlike a portfolio project, that advantage is
legible from your CV alone.

This also makes the §4 project sharper: **build the ICP model for a contech product**, filtering
Companies House to construction SIC codes (41–43) in the Thames Valley. You then arrive at a
contech company with a target list of their actual market. That is a much stronger opening than
any analysis in the current repo.

---

## 5. Berkshire, IPA and EPC — re-scored

All three proposals from the previous audit lose value here, because none demonstrates commercial
ability.

- **Berkshire new-build premium (6–7h)** — build it **only** if you commit to proptech targeting,
  and if so build it *after* the ICP project. It gives you market fluency to open a conversation
  with a proptech founder. It does not evidence anything either of you needs from the role.
- **IPA major projects (5–7h)** — **drop.** Interesting, unverified data access, and it speaks to
  policy analysis rather than anything commercial.
- **EPC × Price Paid join (12–18h)** — **drop for now.** It was the technically ambitious option
  under the old brief. Under this one you'd spend three days on address matching to demonstrate a
  skill none of the three tracks hires for. Keep it as a dissertation idea.

---

## 6. Critical path

Assumes the ~15 hours from your original brief; §6.3 covers 30–45.

### 6.1 First two hours — unchanged from `AUDIT.md`, for changed reasons

| # | Task | Min |
|---|---|---|
| 1 | ~~Delete `Customer_Segmentation/` and purge from history (`AUDIT.md` §8).~~ **DONE** | 40 |
| 2 | ~~Delete the 2-byte `.pbix` and `sql_queries_eda.sql`; strip both from the e-commerce README.~~ **DONE** (the README's pipeline diagram now documents the real stages 4–6) | 20 |
| 3 | ~~`git add` the two churn notebooks — still untracked, still invisible.~~ **DONE**, and notebook 6 with them. | 5 |
| 4 | `git mv "Ecommerce Data Analytics" ecommerce-analytics` | 5 |
| 5 | Rewrite the root README on the §7 structure. **Drop the "BI Analyst application to Shopee" framing** — under these tracks it is an argument for a different job. | 30 |
| 6 | ~~Confirm the BYD CNY/USD diagnosis yourself in notebook 05.~~ **DONE** — confirmed empirically: `BYDDY.info` returns `financialCurrency=CNY`, `currency=USD`. | 20 |

### 6.2 Hours 2–15

| Hours | Task |
|---|---|
| **2–4** | **DONE (6 Sep).** ~~Fix every numeric contradiction in Financial Analysis.~~ All five closed. The P/E reconciles to 189.3×, not the 188× §7 predicted — see §0.2. |
| **4–5** | **DONE (6 Sep).** ~~Proofread the SCIR notebook properly.~~ Rewritten — the corrected figures broke the BYD and Ford arguments, not just their numbers. |
| **5–12** | **Build the Companies House ICP project** (§4), including the three example outbound emails. Construction SIC codes if going the contech route. |
| **12–15** | **DONE (6 Sep).** ~~Finish churn steps 3–4~~ as an ROI case: threshold sweep, expected £ against the no-model 90-day rule, one chart, one sentence of result. Publish it even if the model loses to the rule — "the simple rule wins, so use the rule" is a strong commercial finding. |

**Deliberately not in the 15 hours:** re-running the blank e-commerce notebooks, exporting the
Plotly charts, and the Berkshire project. All were in the previous plan; all lose to the ICP
project and the churn ROI case under this brief.

### 6.3 If you have 30–45 hours

- **+3h — export the Plotly charts to PNG** (`AUDIT.md` §8), so Financial Analysis stops showing
  six blank gaps. **Still open** after the 6 Sep work — the charts render only in a live kernel.
- ~~**+30 min — run the two blank e-commerce notebooks** and commit with outputs.~~ **DONE (6 Sep)** — and notebooks 3, 4 and 5 re-run with them, so all six are reproducible from `get_data.py`.
- **+6–8h — deploy one artefact.** A Streamlit app over the ICP model where a visitor picks a
  region and SIC code and gets a ranked account list. **For Track 3 this is the highest-value item
  in this document after the fixes** — Solutions Engineering is demonstrated by a thing that runs,
  not a notebook that describes one. Streamlit Community Cloud hosts it free from a public repo.
- **+2h — record a 3-minute Loom** walking through the ICP model as if presenting to a sales team,
  and link it at the top of the README. This is the only artefact in the entire plan that directly
  evidences the skill all three tracks actually hire for: explaining something to someone who
  won't read the detail. For its cost it is the best value here.
- **+6–7h — Berkshire**, only under proptech targeting.

At 45 hours, do all of the above and stop. Further hours belong in the dissertation.

---

## 7. README rewrite plan

### Root README

The current opening argues for an analyst job. Rewrite so that a founder or sales manager reaches
"commercial" before "analytics".

```markdown
# Lee Keet Men

Civil engineer turned BI analyst — two years building production dashboards and reporting
at Shopee Malaysia, trained in applied AI through the Gamuda AI Academy (an applied AI
programme run by a Malaysian infrastructure and construction group). Starting an MSc in
Applied AI for Business at Henley Business School, University of Reading, September 2026.

I'm looking for commercial roles where the technical background is an edge rather than a
detour — early-stage sales, solutions engineering, and anything selling to technical or
construction buyers, where being able to talk to the buyer in their own language matters.

---

### 🎯 [Who should we call first?](./icp-model/) — target account model
Which UK construction SMEs are the best-fit prospects for a contech product, and why them first?
**Scored and ranked 1,200 companies from Companies House data down to a 25-account list —
with three outbound emails written from it.**
[chart] · [3-minute walkthrough](loom-link)

### 📉 [Is it worth paying to keep a customer?](./ecommerce-analytics/) — churn and retention
Which customers are about to stop buying, and does contacting them pay for itself?
**No: against a tuned silence rule the model is worth £0.23 a customer. But given only 100 calls to
make, ranking by probability × value at risk returns £7,132 against the rule's £4,022 — while
ranking by probability alone does worse than random.**

### 📊 [Is Tesla's valuation justified?](./financial-analysis/) — comparative thesis
A structured view on three EV manufacturers using Situation–Complication–Implication–Risk.
**The market pays ~189× earnings for Tesla against ~18× for BYD and ~6× for Ford — while Tesla
generates the least free cash flow of the three.**
```

Three deliberate choices. Every project title is a **question a commercial person would ask**, not
a technique. The ICP project sits first because it's the one that matches the job. And "trained in
applied AI by a construction group" stays in line one — for contech and proptech employers that is
the sentence that gets the reply.

### Per-project

Structure unchanged from `AUDIT.md` §7 — question, answer with a number, image, reproduce, what I'd
do differently — with **one addition for these tracks: a "So what would you do about it?"
section.** Two or three sentences on the action a business should take. Analyst readers infer it;
commercial readers are hiring for exactly that step and will not infer it on your behalf.

**Drafted lines, from what's verified in the repo:**

- **Financial Analysis** — ~~*not yet writable*~~ **written, 6 Sep**, and not as drafted. The
  currency fix showed Ford, not BYD, to be the largest cash generator, so the drafted clause
  "BYD generating more free cash flow" would have carried the original error forward in softer
  language. The line that survives contact with the corrected data:
  *"The market pays ~189× earnings for Tesla against ~18× for BYD and ~6× for Ford — while Tesla
  generates the least free cash flow of the three."* See §0.2.
- **Churn** — ~~*not yet writable*~~ **written, 6 Sep.** AUC 0.744 is not a commercial answer; the
  cost sweep and the swept-rule benchmark produce one. See §0.1 for the line.
- **E-commerce** — verified in notebook 3, with one figure corrected on 6 Sep: *"Returning customers
  are worth 6.9× a one-time buyer (£2,867 vs £416) and generate 92.8% of revenue; 21.4% of products
  drive 80% of revenue."* (The 21% came from a denominator that double-counted products — see §0.1.)
- **ICP model** — to be written.

**All three existing projects now have a line 2** (was two missing, then one; Financial Analysis closed the last on 6 Sep — only the unbuilt ICP project is outstanding). That was a finding under the old brief
and it's a sharper one here: for these roles the number *is* the pitch.

---

## 8. Honest verdict

**Track 1 — SDR/BDR: mildly negative, and mostly irrelevant.** Four managers in five never look.
The fifth sees a technical portfolio with an analyst application stated on the landing page and
prices in flight risk. The repo isn't your lever here — your CV, your email and your phone manner
are. Two hours of deletion plus a rewritten README makes it neutral; the ICP project makes it a
genuine asset, because it shows you doing the job unprompted. Don't spend more than that on this
track.

**Track 2 — Founder's Associate: negative today, and the most fixable.** The role selects for
closing loops, and the repo is a museum of open ones — a 404ing dashboard link, blank notebooks,
invisible charts, uncommitted best work, a README that miscounts its own contents. The underlying
range would genuinely impress this reader. He'll never reach it. The good news is that the fix is
mostly deletion and finishing, not building: this track's verdict flips from negative to positive
in about twelve hours.

**Track 3 — Solutions Engineer: the only track where it helps today, and the one with the highest
ceiling.** The technical credibility is real and the instinct for stating limitations honestly is
a genuine pre-sales asset that most graduates lack entirely. Two things held it back. ~~The numeric
contradictions are disqualifying in a role whose whole function is being the person whose numbers
are right — three different P/E figures for one company is the specific failure this job prevents.~~
**Closed 6 Sep (§0.2)** — and the fix improved on the brief: the corrected analysis states which of
its own conclusions changed and why, which is a stronger pre-sales signal than never having erred.
The remaining constraint is that notebooks are the wrong medium: this reader wants something that runs and a person who can
explain it. Fix the numbers, deploy one thing, record one Loom, and this becomes a strong
application.

**Across all three:** the repo's problem is no longer that it's broken. After two hours it won't
be. The problem is that it's a **portfolio for a job you're no longer applying for.** Fixing the
defects makes it honest; only the ICP project makes it relevant.

**One line:** ~~delete `Customer_Segmentation` today, fix the numbers in Financial Analysis this
week,~~ **both done (§0.1, §0.2)** — now build the Companies House target-account model — and aim the applications at contech
and proptech companies, where your engineering background is a commercial advantage rather than a
detour to explain away.

---

Sources: [Companies House Free Company Data Product](https://resources.companieshouse.gov.uk/infoAndGuide/faq/publicDataProduct.shtml) · [CH Guide — companies bulk data](https://chguide.co.uk/bulk-data/companies)
