# Portfolio projects

Four end-to-end projects, each taking a question from raw data to a decision someone could act on.

**[UK Tech Outbound](UK%20Tech%20Outbound/)** — Which UK property developers should a sales team call
first? An ideal-customer-profile and target-account model over the Companies House public register:
5.7 million companies narrowed to a segment, ranked by a transparent four-component score, and ending
in three outbound emails that each cite a specific fact about the company they are addressed to.
**136,542 sellable accounts ranked, with 19,565 sibling SPVs folded into their parent developers.**
*Python, pandas, 42 tests.*

**[Ecommerce Data Analytics](Ecommerce%20Data%20Analytics/)** — Is it worth paying to keep a customer?
ETL pipeline design, customer lifetime value modelling and churn analysis on transactional retail data,
with the cost of a churn model benchmarked against a naive rule. **With unlimited contacts the model is
worth £0.23 a customer; with 100 calls to make, ranking by probability × value at risk returns £7,132
against the rule's £4,022.**
*Python, pandas, Jupyter.*

**[Financial Analysis](Financial%20Analysis/)** — Is Tesla's valuation justified? Comparative financial
analysis of Tesla, BYD and Ford from SEC EDGAR filings, covering earnings quality, valuation and a
written investment thesis. **The market pays about 189x earnings for Tesla, 18x for BYD and 6x for
Ford, while Tesla generates the least free cash flow of the three.**
*Includes a reusable EDGAR client with unit tests.*

**[Student Engagement Analysis](Student%20Engagement%20Analysis/)** — Is early activity on an
online course site a usable early warning sign for withdrawal? Logistic and linear regression over
the Open University Learning Analytics Dataset: 32,593 student records across 22 module-presentations,
with the half of withdrawals whose engagement window was cut short by the withdrawal itself held out
of the sample rather than left to overstate the result. **Each extra 100 clicks in the first month is
associated with 11% lower odds of withdrawing and 28% higher odds of passing.**
*Python, statsmodels, odds ratios with confidence intervals.*
