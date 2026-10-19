# Acquirepad UK: ideal customer profile

**Vendor.** Acquirepad is the AI-native operating system and data layer for the real estate industry. It automates workflows across acquisitions, research, document preparation, financial calculations, capital raising, portfolio management, debt tracking, commercial leasing, reporting and sales, and integrates with the rest of the real estate software stack. It does not sell point AI tools.

**Buyer.** Its named customers are mid-sized German investment and asset managers, and it has customers in
France, the Netherlands, Poland and Sweden. The UK entry question is which UK buyers of commercial property
run enough of those functions in-house to need one operating system,
and are active in the UK now. A link to Acquirepad's existing network helps, but it is a tie-breaker, not a requirement.

**UK terms.** The UK equivalent of the German exposé is the agent's information memorandum (IM).

## Scoring

Each firm is scored 0 to 3 on six dimensions. The weighted total is out of 100:

```
total = sum( weight[d] * score[d] / 3 )   for the six dimensions
```

A fact that cannot be verified from a public source scores 0 and is marked "unverified". So a low score
can mean "weak fit" or "no public evidence". The sources column shows which one applies.

The window for deal flow and triggers is the 12 months to 19 October 2026, the research date.

**Freshness rule.** Events (deal flow and triggers) must fall inside that 12-month window. Slower facts
(segment, size, operating breadth, warm path, first moves and systems) need a source from the last three
years, so dated on or after 19 October 2023, or a live company or vendor page that describes the firm as it
is now. Anything older counts only if a fresh source backs it up. Otherwise the score drops to what current
evidence supports.

The weights live in one place, `WEIGHTS` in `score.py`. Change them there and re-run `python score.py`.

| # | Dimension | Weight | Why this weight |
|---|---|---|---|
| 1 | Segment fit | 20 | The wrong type of firm cannot buy, however strong the other signals are. A UK commercial property buyer is the whole point of a UK entry. |
| 2 | Size fit | 5 | Mid-market is where a founder can reach the decision maker, but the size evidence is coarse. |
| 3 | Deal flow | 15 | More UK IMs and rent rolls mean more data to share across teams. Partly overlaps with active capital in the trigger. |
| 4 | Operating breadth | 15 | One operating system pays off when one firm runs many functions. Integrated firms feel the gaps between tools most. |
| 5 | Trigger | 35 | The strongest single signal. A new fund, owner, team or UK deal is when systems get chosen, and it gives a reason to call this month. |
| 6 | Warm path | 10 | A link to Acquirepad's network makes an intro easier, but the UK entry does not depend on it. |
| | **Total** | **100** | |

## Rubric

**1. Segment fit**
- 3: Private equity real estate investor, investment manager or asset manager whose main business is buying UK commercial real estate.
- 2: Real estate investor that buys UK commercial property as one part of a wider strategy (for example a pan-European manager, a REIT or a family office with a property arm).
- 1: Adjacent. Buys UK property, but mainly residential, development-led or lending.
- 0: Not a buyer of UK commercial property, or unverified.

**2. Size fit**
- 3: Mid-market. Roughly £1bn to £20bn real estate assets under management, or a clearly focused UK team.
- 2: Smaller (under £1bn) but active, or larger (£20bn to £50bn) with a distinct UK team.
- 1: Very small, or a large manager where the UK deal team sits inside a global platform.
- 0: Largest global managers (for example Blackstone, Brookfield) or unverified. These are excluded from the target list.

**3. Deal flow**
- 3: Three or more UK acquisitions or disposals in the last 12 months, with sources.
- 2: Two in the last 12 months.
- 1: One in the last 12 months, or regular UK deals in the prior two years.
- 0: None found, or unverified.

**4. Operating breadth** (how many of Acquirepad's functions the firm runs in-house)
- 3: Vertically integrated. Investment and asset management in-house, plus property management or letting in-house, or the firm describes itself as fully integrated.
- 2: Investment plus asset or portfolio management in-house. Property management outsourced or not evidenced.
- 1: Investment only, or an externally managed vehicle, or day-to-day management run by operating partners.
- 0: Unverified.

**5. Trigger** (last 12 months). Built from three parts, capped at 3:
- **Event, 0 to 2.**
  - 2: New UK fund, mandate or platform with capital committed, a new head of UK or UK office, first UK deals for a pan-European strategy, or a change of owner that brings new capital.
  - 1: A senior UK hire outside acquisitions, or an announced strategy or capital raise without a close.
- **Active capital, +1.** A UK acquisition, or a fund close with a confirmed UK allocation, in the last 12 months. Deals outside the UK do not count.
- **Data, digital or innovation hire, +1.** A named hire into one of those roles in the last 12 months.

**6. Warm path**
- 3: German-owned or German-backed. A German parent or owner, or a German manager itself.
- 2: A German partner, co-investor or sister company directly named, German operations, a direct link to Acquirepad's team or customers, or a parent in a market where Acquirepad already has customers (France, the Netherlands, Poland, Sweden).
- 1: Other continental European parent (for example Swiss or Belgian).
- 0: UK or non-European ownership only, or unverified.

## Version 2 (18 October 2026)

Updated after Acquirepad's LinkedIn posts repositioned it from point AI tools to a shared data and
workflow layer. Operating breadth was added. Trigger now rewards active capital and data hires. Warm path
now separates German-owned firms from other European ones. Weights moved from deal flow towards breadth,
trigger and warm path.

## Unscored columns

- **first_move:** the entry point (a named person only where a recent public source names them), the angle, or the intro route.
- **systems:** property systems the firm is known to run. Acquirepad lists Yardi, SAP, Salesforce, HubSpot and Dealpath among its integrations, so a known system shapes the pitch and the likely objection.

Both need a source URL, like any score. `score.py` checks this.

## Version 3 (18 October 2026)

- Process pain removed. Only 1 of 27 firms had any evidence, so it added weight without information. Its 5 points moved to operating breadth.
- Checked against the customers with published stories on Acquirepad's site: GIEAG, HT Group, GARBE, Hines, Advenis, KRE Group, GPEP and WERTCONTOR. None of the 27 firms is among them.
- Customers used as routes in. GARBE sold Redevco a Duisburg logistics park in September 2026, so Redevco moved to warm path 2. Advenis, a French SCPI group, is the reference for French SCPI buyers.
- Two customers are UK expansion accounts, not targets: Hines bought three UK retail parks in September 2026, and Advenis launched its Eden SCPI with the UK as a target market.
- Swiss Life AM UK moved to warm path 2: Acquirepad's team lists Swiss Life experience.

## Version 4 (18 October 2026)

- Active capital now counts UK deals only. Union Investment (a Swedish retail park), Catella APAM (a Dublin purchase), Sirius (a German business park), Redevco (a European fund with no confirmed UK allocation) and Sofidy (acquisitions not broken down by country) lost the point. Each now shows "No UK trigger found".
- The page shows the top 15 firms.

## Version 5 (18 October 2026)

- Trigger weight raised from 20 to 35, so the page favours firms with a reason to call now. Size, deal flow and operating breadth gave up the points. Of the top 15, 14 now have a UK trigger. Union Investment is the exception and stays on the strength of its German ownership.
- Acquirepad's company description says it works with real estate companies in Germany, France, the Netherlands, Poland, Sweden and other European markets. Source: [University of Reading TargetConnect employer page](https://reading.targetconnect.net/student/employers.html?employer=484319&page=employer) (login required, seen 17 October 2026). French parents (Iroko, Corum, Remake, Sofidy) moved from warm path 1 to 2. Advenis, a French group, is on Acquirepad's customer page.

## Version 6 (19 October 2026)

- Warm path cut from 20 to 10. Acquirepad is expanding into the UK, so a firm's UK fit and UK activity matter more than whether it is German-owned. Segment rose to 20 and deal flow to 15.
- All 15 firms on the page now have a UK trigger. Deka and Union Investment dropped off; Custodian and Greenridge, UK managers buying now, came on.
- The German links play was replaced with "UK managers buying often". German intro routes remain in the First move column.

## Version 7 (19 October 2026)

- Added the freshness rule above. Five scores rested only on evidence more than three years old and were cut to what current sources support: Corum operating breadth 3 to 1, Iroko 3 to 2, NewRiver 3 to 2, Custodian 1 to 0, Clearbell size 2 to 0. AshbyCapital's size (a 2016 figure) also went to 0.
- Old sources replaced with fresh ones where they exist: Catella APAM's size now cites Catella's Q2 2026 presentation (SEK 16bn), Swiss Life's size a WealthBriefing article of 6 October 2025, and Chancerygate's breadth IREI, 31 July 2026.
- System claims older than three years were removed: Chancerygate (Coyote, MRI; 2022), HIH (cloudbrixx; 2022) and Clipstone (Yardi; 2023). NewRiver's Yardi claim stays, sourced to Yardi's live client-story page.
- Custodian dropped off the page and Deka came on. All 15 firms on the page still have a UK trigger.

## What the score is not

It ranks a first call list. It is not a qualification decision. A firm that scores well still has to show
budget, a named owner of its data and workflow, and interest in a shared platform on a first call.
