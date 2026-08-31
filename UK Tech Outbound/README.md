# 🚀 Data-Driven UK GTM Pipeline Engine (Reading & London Tech Hubs)

## 📌 Commercial Value Proposition
Modern outbound B2B sales cycles fail due to inaccurate prospecting and broad, unpersonalized targeting. This repository hosts an automated Revenue Operations (RevOps) pipeline engineered to dynamically scrape, enrich, and prioritize B2B accounts along the UK’s M4 tech corridor (London/Reading) using the live UK Companies House API.

By converting raw corporate filing data into a clean, prioritized **Outbound Account Tiering Matrix**, this engine replaces manual lead sourcing, reducing Customer Acquisition Costs (CAC) and accelerating Pipeline Velocity.

---

## 📊 Analytical Architecture & Lead Scoring Logic

The pipeline screens prospects through a 3-layer heuristic matrix to score lead viability on a 0-100 scale:

*   **Industry Intent Vector (40%):** Validates company alignment with high-value technology, SaaS, and engineering Standard Industrial Classification (SIC) codes (e.g., 62010 for computer programming).
*   **Scale Lifecycle Signal (40%):** Targets companies between 2 and 5 years old. This identifies scale-ups navigating high-growth inflection points who need external technological solutions.
*   **Operational Health Proxy (20%):** Evaluates accounts filing history integrity to instantly disqualify financially distressed entities.

---

## 🛠️ Technical Stack & Frameworks
*   **Data Pipeline & Logic:** Python 3.11 / REST API Integration
*   **Transformation & Analysis:** Pandas / NumPy
*   **Output Vectorization:** Structured CRM-ready CSV Pipeline / Automated Outreach Generation Trigger Logic

---

## 📈 Actionable Business Outcomes
1. **Zero Cold Lists:** Automates the elimination of dissolved or unviable accounts before a salesperson opens an email.
2. **Context-Driven Sales Triggers:** Programmatically appends an outbound hook (e.g., location clustering or technical focus) to every lead record, ensuring high-conversion messaging personalization.
3. **Optimized Sales Unit Economics:** Empowers a high-agency commercial team to focus 100% of their daily 20-hour capacity on tier-1 priority targets.
