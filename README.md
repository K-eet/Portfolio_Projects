# Portfolio projects

Four end-to-end projects, each taking a question from raw data to a decision someone could act on.

**[Ideal Customer Profile project](Ideal%20Customer%20Profile%20project/)**: which accounts should a
sales team call first? An ICP and target-account model over the Companies House register: 5.7 million
companies narrowed to a segment, ranked by a transparent four-part score, and ending in three outbound
emails that each cite a specific fact about the company they are addressed to.
*Python, pandas, 42 tests.*
- **Case study: [Acquirepad UK target accounts](Ideal%20Customer%20Profile%20project/case_studies/acquirepad_uk/).**
  The same method applied by hand: 27 UK commercial real estate investors researched for a Berlin
  proptech entering the UK. Every score above zero carries a source, and each firm on the
  [one-page list](Ideal%20Customer%20Profile%20project/case_studies/acquirepad_uk/outputs/acquirepad_uk_targets.pdf)
  has a first move.

**[Student Engagement Analysis](Student%20Engagement%20Analysis/)**: is early activity on an online
course site a usable early warning sign for withdrawal? Logistic and linear regression over the Open
University Learning Analytics Dataset: 32,593 student records across 22 module-presentations. Half of
withdrawals had their engagement window cut short by the withdrawal itself, so they are held out of the
sample rather than left to overstate the result.
*Python, statsmodels, odds ratios with confidence intervals.*

**[Ecommerce Data Analytics](Ecommerce%20Data%20Analytics/)**: ETL pipeline design, customer lifetime
value modelling and churn analysis on transactional retail data, with the cost of a churn model
benchmarked against a naive rule.

**[Financial Analysis](Financial%20Analysis/)**: comparative financial analysis of Tesla, BYD and Ford
from SEC EDGAR filings, covering earnings quality, valuation and a written investment thesis.
*Includes a reusable EDGAR client with unit tests.*
