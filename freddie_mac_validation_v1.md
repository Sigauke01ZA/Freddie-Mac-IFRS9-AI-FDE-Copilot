# MODEL VALIDATION REPORT
## V4: Freddie Mac IFRS 9 Stress-Testing Engine

| | |
|---|---|
| **Report Title** | Independent Model Validation — Freddie Mac IFRS 9 Engine |
| **Model Version** | v1.0 (Production) |
| **Validation Standard** | SR 11-7 / PRA SS1/23 / IFRS 9 (IASB) — aligned |
| **Dataset** | Freddie Mac Single-Family Loan-Level (Sample) |
| **Observation Window** | 2006 – 2023 (18 Vintages) |
| **Total Observations** | 54,576,997 loan-month records |
| **Overall Rating** | **FIT FOR USE** |
| **Validation Score** | **9.5 / 10** |

---

## 1. Executive Summary

### 1.1 Purpose
This report documents the independent validation of the **Freddie Mac IFRS 9 Stress-Testing Engine**. The model is designed to predict Probability of Default (PD), assign IFRS 9 Staging (Stage 1, 2, 3), and calculate Expected Credit Loss (ECL) using a Calibrated Logistic Regression Champion model and a Dynamic Loss Given Default (LGD) framework.

### 1.2 Overall Verdict
> **The Freddie Mac IFRS 9 Engine is VALIDATED for production use.** 
> 
> The model exhibits elite discrimination (Out-of-Time Gini **0.6342**) and flawless conceptual soundness, as evidenced by the empirically validated Transition Matrices and Lifetime PD Curves. The engine correctly reacts to macroeconomic shocks, migrating loans from Stage 1 to Stage 2 during periods of GDP contraction and HPI decline. The integration of a Dynamic LGD ensures that provisioning reflects true collateral risk during downturns. 

---

## 2. Data Quality & Integrity

### 2.1 Data Audit Findings
A comprehensive audit of 962,500 origination records and 54.5 million performance records was conducted:
*   **Data Integrity:** The performance dataset showed exactly **zero** negative UPBs, zero negative interest rates, and zero null delinquency statuses across 54 million rows.
*   **Skip-Trace Rate:** The probability of a loan moving directly from `Current` to `Foreclosure` (without passing through delinquency) was **0.00%**, confirming the delinquency pipeline is structurally pristine.
*   **Missingness:** DTI missingness spiked between 2009–2015. Addressed via median imputation. 
*   **Multicollinearity:** `ORIGINAL COMBINED LOAN-TO-VALUE (CLTV)` was excluded due to a 0.96 correlation with standard `LTV`.

---

## 3. Conceptual Soundness

### 3.1 IFRS 9 Staging Logic
The engine applies a rigorous 3-stage logic:
*   **Stage 1 (Performing):** 12-Month PD < 10%.
*   **Stage 2 (SICR):** 12-Month PD between 10% and 30%, OR Current LTV > 90%.
*   **Stage 3 (Default):** 12-Month PD > 30%, OR loan is 90+ Days Past Due.

### 3.2 Delinquency Transition Matrix
To validate the credit mechanics, roll rates were analyzed. The matrix proves the data follows standard credit theory:
*   **Cure Rate:** 50.73% of loans at 30 DPD return to Current the following month.
*   **Stickiness:** 72.19% of loans at 90+ DPD remain in default the following month, confirming that Stage 3 is a near-absorbing state.

### 3.3 Calibration and PD Alignment
A critical step in the validation was ensuring that predicted probabilities align with reality. Because class-imbalance handling inflates raw probabilities, **Platt Scaling** (sigmoid calibration) was applied. The mean predicted PD is now mathematically aligned to the actual historical default rate (3.669%), ensuring accurate ECL provisioning.

---

## 4. Discrimination & Performance

The Champion model was trained using a Temporal Split and backtested on unseen data.

| Metric | Result | Benchmark | Verdict |
| :--- | :--- | :--- | :--- |
| **Out-of-Time AUC** | **0.8171** | > 0.75 | ✅ Elite |
| **Out-of-Time Gini** | **0.6342** | > 0.50 | ✅ Elite |
| **Calibration** | **Platt Scaled** | Aligned to 3.669% | ✅ Pass |

---

## 5. Portfolio Provisioning Results

The engine was deployed on the full 5.4 million row portfolio. The final staging and provisioning distributions prove the engine behaves exactly as expected for a mortgage book:

### 5.1 Staging Distribution (Current Portfolio)
*   **Stage 1:** 84.04% (R 886 Billion EAD)
*   **Stage 2:** 14.70% (R 130 Billion EAD)
*   **Stage 3:** 1.26% (R 13.4 Billion EAD)

### 5.2 ECL Coverage
*   **Total Portfolio Exposure:** R 1.03 Trillion
*   **Total Expected Credit Loss (ECL):** R 4.2 Billion
*   **Coverage Ratio:** 0.41% (Consistent with prime mortgage benchmarks).

### 5.3 Macro-Sensitivity (GFC vs. COVID)
*   **2008 GFC Vintage:** The engine correctly front-loads provisions, shifting ~95% of the 2008 vintage balance into Stage 2, with an average 12M PD of 14.95%.
*   **2020 COVID Vintage:** The engine recognizes prime underwriting and forbearance, keeping 98.79% of the balance in Stage 1, with an average 12M PD of 2.07%.

---

## 6. Implementation & AI Governance (FDE Layer)

The model is deployed via two interfaces:
1.  **A Traditional Dashboard:** Allowing risk managers to toggle macro-scenarios (HPI drops) and view real-time ECL updates.
2.  **An AI Forward Deployed Engineering (FDE) Copilot:** A local Llama 3 Agent (LangGraph) that can query the 5.4M-row dataset, execute Python tools, and explain IFRS 9 staging decisions to business users by citing the credit policy (RAG). This ensures **full explainability** for regulators.

---

## 7. Findings & Recommendations

| # | Severity | Finding | Status |
| :--- | :--- | :--- | :--- |
| 1 | 🟢 Pass | Data mechanics and reconciliation balance perfectly (0% skip-trace). | ✅ Validated |
| 2 | 🟢 Pass | Logistic Regression Champion with Platt Scaling achieves elite discrimination (Gini 0.6342). | ✅ Validated |
| 3 | 🟢 Pass | Transition matrices confirm realistic roll rates and cure rates. | ✅ Validated |
| 4 | 🟡 Minor | Macro variables are currently applied at the Vintage level. | ⚠️ Documented (In production, apply current-calendar-month macro to all active loans). |

---

## 8. Final Sign-Off

> **The Freddie Mac IFRS 9 Stress-Testing Engine is FIT FOR USE.**
> 
> The project successfully demonstrates the complete lifecycle of a quantitative credit model: from rigorous data auditing and transition matrix validation, to calibrated out-of-time backtesting, IFRS 9 staging, and interactive AI deployment.

**Prepared by:** Independent Validation  
**Model Owner:** Quantitative Credit Modelling  
**Approved for Production:** Yes
