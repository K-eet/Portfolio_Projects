# Theory — what this project is doing, and why

A plain-language walkthrough of the churn project: the reasoning behind each step, using the
numbers this repo actually produced. Written to be read straight through.

---

## 0. Where things stand right now

| | State |
|---|---|
| Notebook 4 — define churn | **Done.** Evidence laid out, threshold chosen (90 days) |
| Notebook 5 — temporal split + baseline | **Done.** Logistic regression, AUC 0.744 |
| Notebook 6 — cost and benchmark | **Done.** The money result is in section 6 below |

All three churn notebooks are committed, and the README carries the result. The analysis is
complete: the sequence runs from "there is no label" to a number a business could act on.

Also done earlier, outside the analysis: deleted the `Customer_Segmentation` folder and purged it
from git history, removed the empty `.pbix` and the orphan SQL file, and wrote a bounded scope
into `CLAUDE.md` with a "Someday" list so the last step couldn't sprawl. It didn't.

---

## 1. The problem this project exists to solve

**Which customers are about to stop buying, and is it worth spending money to keep them?**

The second half of that question is the whole point. Predicting churn is a modelling exercise.
Deciding whether to act on the prediction is a business decision, and it's the part almost every
portfolio churn project skips.

---

## 2. The first hard part: there is no churn label

In a **contractual** business — Netflix, a gym, a phone contract — churn is an event. Someone
cancels. There's a row in a database with a date on it. You can point at it.

Retail is **non-contractual**. Nobody announces they're leaving. They just stop coming back. So
the dataset contains no column saying who churned, and no amount of cleaning will produce one.

**You have to invent the label.** That means deciding how many days of silence counts as "gone" —
and that decision is a piece of analysis in its own right, not a preliminary you rush past. Change
the threshold and you change who counts as a churner, which changes the model, which changes the
answer.

This is why notebook 4 exists at all. Most Kaggle churn projects don't have this notebook, because
their dataset shipped with a `Churn` column somebody else invented. Yours doesn't, and that's an
advantage — it's the step that shows judgement rather than technique.

---

## 3. How the threshold was chosen

### The idea

Don't pick a round number. Look at how customers actually space out their purchases, then set the
threshold somewhere that's clearly *unusual* for them.

### Two ways to measure "typical spacing", and why both are shown

Notebook 4 reports the gap between consecutive purchases two different ways. This distinction is
subtle and worth understanding, because it's the kind of thing an interviewer can probe.

**Pooled gaps** — throw every gap from every customer into one pile:

| Percentile | Days |
|---|---|
| 50th | 28 |
| 75th | 58 |
| 90th | 110 |
| 95th | 155 |

**Each customer's own median gap** — work out each customer's typical spacing first, then look at
the distribution of *those*:

| Percentile | Days |
|---|---|
| 50th | 52 |
| 75th | 97 |
| 90th | 166 |
| 95th | 224 |

The pooled median is 28 days. The per-customer median is 52 days. Nearly double. Why?

**Because pooling over-weights frequent buyers.** Someone who bought 50 times contributes 49 gaps
to the pile. Someone who bought twice contributes 1. So the pooled figure is dominated by your
most active customers and makes the business look faster-moving than it is for a typical customer.
The per-customer view gives every customer one vote.

Neither is wrong. They answer different questions — *how fast does this business turn over?* versus
*how fast does a typical customer buy?* — and for setting a churn threshold, the second is the
relevant one, because the threshold has to be fair to an ordinary customer.

### Why 90 days

Four reasons, weakest to strongest is the wrong order, so here they are as they actually rank:

**1. It matches the benchmark.** Step 4 compares the model against the obvious no-model rule:
*contact everyone silent for 90 days.* If the label said 120 days while the rule fired at 90, the
two would be answering different questions and the comparison would be meaningless. This is the
decisive reason — and note it comes from how the comparison is set up, not from the data. Worth
being upfront about that.

**2. 90 days is genuinely unusual behaviour.** It sits between the 75th (58d) and 90th (110d)
percentile of pooled gaps, and just under the 75th percentile of customers' own median gaps (97d).
So for roughly seven customers in ten, 90 days of silence is longer than their own normal rhythm.
Unusual, but not yet certain — which is what you want from an early warning.

**3. More positives to learn from.** 571 repeat customers get labelled churned at 90 days, against
412 at 120. And the observation window stays longer (283 days vs 253), so the features have more
history behind them.

**4. It leaves time to act.** A label that's more certain but arrives later is less useful. The
point of prediction is room to intervene.

**The cost, stated honestly:** 90 days catches more people who were never actually leaving. Those
false alarms cost real money. That isn't an argument for 120 — it's an argument for *pricing* the
error rather than debating it, which is exactly what step 3 does.

---

## 4. The second hard part: not cheating with time

This is the step most people get wrong, and it's the one that would embarrass you in a technical
interview if you couldn't explain it.

### The trap

The obvious approach: compute features for every customer (how recently they bought, how often,
how much), then split randomly into 70% train and 30% test.

**This is broken.** Here's why.

Churn is *defined* by silence at the end of the data. If you compute a customer's "recency" using
the whole dataset, that recency figure already tells you whether they churned — because churn is
literally "recency greater than 90 days". You've handed the model the answer inside the question.

You'd get a beautiful AUC near 1.0 and you'd have learned nothing. The model isn't predicting; it's
reading the label off a feature. This is called **leakage**, and it's the single most common way
churn projects are quietly worthless.

### The fix: a snapshot

Pick a date and cut the data in two.

```
2010-12-01                        2011-09-10                    2011-12-09
    |                                  |                              |
    |------ OBSERVATION WINDOW --------|----- OUTCOME WINDOW ---------|
    |         283 days                 |        90 days               |
    |                                  |                              |
    features built ONLY from here      label read ONLY from here
```

The snapshot date **C** is `end_date − 90 = 2011-09-10`.

- **Features** (recency, frequency, tenure, spend, average gap) use only data on or before C.
- **Label** — did they buy at all after C? No purchase in the outcome window = churned.

Now the model genuinely has to predict. At the snapshot, it sees a customer's behaviour to date
and nothing else, and it has to guess about a future it can't observe. That's the real task.

### Why the assertions matter

Notebook 5 contains this:

```python
assert obs["day"].max() <= C, "observation data past the snapshot"
```

That's a runnable check that the leak didn't happen. If someone later edits the code and
accidentally lets future data in, the notebook stops with an error instead of silently producing a
flattering result.

Writing that line is a small thing that signals something big: you know this is where the analysis
breaks, so you built a tripwire. Most candidates don't.

---

## 5. What AUC 0.744 means, and what it doesn't

**AUC** = pick a random churner and a random stayer. How often does the model give the churner the
higher score? That's the AUC.

- 0.5 = coin flip, the model knows nothing
- 1.0 = perfect separation
- **0.744 = real signal, modest strength**

That number is fine. It's roughly what RFM features on retail data should give, and a much higher
number would be suspicious — it would suggest leakage.

**But AUC cannot answer the project's question.** It measures ranking quality. It says nothing
about whether acting on the ranking makes money. A model with AUC 0.9 still loses money if
contacting people costs more than you save. A model with AUC 0.65 can be very profitable if the
customers it finds are worth a lot and contacting them is cheap.

AUC is a diagnostic for you. It is not a result for a business reader — and this project's stated
audience is the business reader.

---

## 6. Step 3: pricing the errors

### Why 0.5 is the wrong cutoff

A classifier outputs a probability. The default is to call anything above 0.5 a churner. That
default quietly assumes **both mistakes cost the same**. Here they clearly don't.

| Mistake | What it costs |
|---|---|
| **False positive** — contact someone who wasn't leaving | one contact, ~£3 |
| **False negative** — miss someone who leaves | their future value, possibly hundreds |

When missing someone is far more expensive than contacting them, **you should contact people you're
only slightly suspicious of.** If a customer is worth £200 and there's a 25% chance an intervention
saves them, then even a 10% probability of churn is worth £5 of expected value — comfortably more
than the £3 it costs to try.

So the cutoff should sit far below 0.5. *How far* is an arithmetic question, not a convention.

### The three assumptions

Rather than researching real figures — which would eat the budget and still be guesses — the
notebook states three assumptions plainly:

1. **Contact cost: £3** per customer
2. **Save rate: 25%** — a quarter of contacted churners are talked round
3. **Value at risk:** `monetary_total × (90 / tenure_days)` — the customer's own historical
   revenue, scaled to a 90-day window

The third is the interesting one. Rather than inventing a customer-lifetime-value model, it uses
each customer's own observed spending rate. Someone who spent £900 over 300 days has a 90-day
run-rate of £270. That's their own history, not an assumption about them.

Being explicit that these are assumptions is the point. A reader can disagree with £3 and re-run
it. A reader can't argue with a number you never showed them.

### The formula

```
expected value = Σ (churned × save_rate × value_at_risk) − £3 × contacts
```

Sweep the cutoff from low to high, compute this at each point, plot it. The peak is the optimal
threshold, and it is nowhere near 0.5.

### What came out

**The optimal cutoff is 0.04.** Not 0.5. Using the default instead costs £17,120 on a test set of
587 customers — it contacts 43 people when it should contact 538.

The arithmetic behind that is one line, and it's worth being able to say out loud. Each customer
has their *own* break-even probability:

```
p* = contact_cost / (save_rate × value_at_risk)
```

For the median customer that's £3 / (0.25 × £523) = **2.3%**. Contacting is so cheap relative to
what a customer is worth that you should chase people you are barely suspicious of. 96.9% of
customers clear their own break-even — which is another way of saying *contact almost everyone*.

**And that's a problem for the model**, because "contact almost everyone" is not a strategy that
needs a model. Hence step 4.

---

## 7. Step 4: the benchmark, and why it's the real result

### The question nobody asks

"Does my model work?" is the wrong question. The right one is:

**"Does my model beat what you'd do without a model?"**

The no-model rule here: *contact everyone who's been silent 90 days.* No machine learning, no
features, one line of SQL. Any competent ops person would do this.

If the rule earns £4,000 and the model earns £4,150, the model is worth £150 — and you'd have to
ask whether that justifies maintaining a model at all. **That gap is the result of this project.**
Not the AUC.

### Sweeping both sides

The original plan compared the tuned model against the rule at a single fixed point. We changed
that: **the rule's threshold gets swept too.**

Why it matters — comparing a carefully optimised model against a rule you didn't bother to tune is
a rigged fight. You'd "win" by handicapping the opponent. Sweeping both is the honest comparison,
and it costs about ten extra lines.

### The rule won — and then the question changed

**The model beats the tuned rule by £136 across 587 customers. That's £0.23 each. It's nothing.**

The gap survives no sensitivity test either: across every combination of contact cost (£1 to £25)
and save rate (10% to 40%), the model's advantage never exceeds £1.51 per customer. Nobody should
run a feature pipeline and a retraining schedule for that.

Worth noting what the *flattering* version of this number would have been. Against the rule fired
at 90 days — the version originally written down — the model appears to win by £13,690. That
number is real, and it would have been easy to report. But it isn't a win for the model; it's a
win for **contacting more people**, which the rule does just as well once you let it fire at 2 days
instead of 90. Sweeping both sides is what turns a £13,690 illusion into a £136 fact.

### But then: the budget

The unconstrained comparison has a hidden assumption — that you can contact as many people as you
like. Under that assumption the answer is trivially "contact nearly everyone", and no *ranking*
can distinguish itself, which is exactly why the model looked worthless.

Real retention teams have a budget: *we can work 100 accounts this quarter.* Then the only thing
that matters is who's at the top of the list, and that's a ranking problem — which is what a model
is actually for. Scoring five rankings on the same test set, at a budget of 100, median over 30
splits:

| Ranking | Median EV |
|---|---|
| **probability × value at risk** | **£7,132** |
| value at risk alone (no model) | £4,956 |
| recency — the no-model rule | £4,022 |
| random | £3,198 |
| probability alone | £2,881 |

Two things there are worth more than the AUC.

**Ranking by churn probability alone is worse than random.** The customers most likely to lapse are
the small, infrequent ones. Spend a scarce budget on them and you protect almost no money. This is
the trap the conventional "deploy the classifier" answer walks straight into, and *no accuracy
metric can see it* — the model with AUC 0.744 is doing exactly what it was trained to do.

**The model only pays once its output is priced.** Multiply the probability by what each customer
is worth and it becomes the best ranking available — beating the rule in 25 of 30 splits by a
median £3,233.

So the finding isn't "the model is useless" and it isn't "the model works". It's:

> The model has no value as a classifier, and real value as a *prioritiser* — but only when its
> probabilities are multiplied by what each customer is worth. Deployed the conventional way, it
> would have performed worse than picking customers at random.

That's a better result than a marginal victory would have been. Knowing when the simple thing
suffices — and spotting the specific condition under which it stops sufficing — is what separates
someone who applies models from someone who sells them.

---

## 8. Why the order matters

Each step is load-bearing for the next:

```
no label exists
      ↓  so you must invent one, defensibly           → notebook 4
threshold = 90 days
      ↓  which fixes the snapshot date at end − 90    → notebook 5
temporal split, leak-free
      ↓  which gives honest probabilities             → AUC 0.744
probabilities that mean something
      ↓  which can be priced against real costs       → notebook 6
optimal contact threshold (0.04, not 0.5)
      ↓  compared against the no-model rule, swept    → notebook 6
gap = £136, i.e. nothing
      ↓  unless the contact budget is finite          → notebook 6
THE RESULT: worthless as a classifier, £3,233 better as a priced prioritiser
```

Get the label wrong and everything downstream is measuring the wrong thing. Leak the future and the
probabilities are fiction, so pricing them is fiction too. This is why the sequence is fixed and
why "do not run ahead" is in `CLAUDE.md`.

---

## 9. Explaining this in thirty seconds

If someone asks what the project is:

> "It's a churn model on UK retail data, but the interesting part isn't the model. Retail has no
> churn label — nobody cancels, they just stop coming — so I had to define churn from how customers
> actually space out purchases, and defend the threshold. Then I split by time rather than randomly,
> because a random split leaks the future into the features and gives you a model that looks great
> and predicts nothing. The model gets AUC 0.744, which is fine but isn't the answer. The answer is
> what happens when you price the two errors — contacting someone costs a few pounds, losing them
> costs their forward value. Do that, and the model beats a plain 'contact everyone who's been
> quiet' rule by about 20p a customer. It's worthless. *Unless* you can only contact a hundred
> people, in which case ranking by probability times value at risk earns roughly three thousand
> pounds more than the rule — while ranking by probability alone, which is what everyone actually
> does, performs worse than picking customers at random."

That paragraph is worth more than the code, and it's the thing to be able to say without notes.
The last sentence is the one that will get followed up on in an interview, so be ready to explain
*why*: the likeliest churners are the smallest customers.

---

## 10. What's left

**The analysis is done.** Notebook 6 closes the sequence, and the README carries the result.

What deliberately wasn't done, and why it would be the wrong instinct: a second model, tuned
hyperparameters, more features. The bottleneck in this project was never model quality. It was the
*economics* — and every one of those three numbers (£3 contact cost, 25% save rate, the run-rate
proxy for value) is an assumption I invented. The conclusion is far more sensitive to whether the
save rate is really 25% than to whether the classifier is logistic regression or gradient boosting.

**So the honest next step is measurement, not modelling:** run the intervention on a holdout group
and find out what a contact actually costs and how many customers it actually saves. That single
experiment would be worth more than any amount of feature engineering — and until it's run, the
right posture towards the £7,132 is that it's an estimate resting on three guesses, stated openly
so a reader can substitute their own.

**The remaining limits, stated plainly:** the save rate is assumed constant across customers when
it almost certainly varies with how far gone someone is; value at risk is a historical run-rate,
not a forecast; the test set is 587 customers with revenue concentrated in a handful of wholesale
accounts, which is why 30 splits are reported rather than one; and the whole thing rests on a
single year of a single retailer's data.
