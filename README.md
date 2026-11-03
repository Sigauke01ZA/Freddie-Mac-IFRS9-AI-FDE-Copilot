# Freddie-Mac-IFRS9-AI-FDE-Copilot
An AI Forward Deployed Engineering (FDE) Copilot built on a 54M-row Freddie Mac dataset. Combines a calibrated IFRS 9 ECL engine with a local Llama 3 agent (LangGraph &amp; ChromaDB) to query 5.4M loans, run macro stress tests, and explain credit policy via RAG.

# Freddie Mac IFRS 9 AI FDE Copilot

An advanced, production-grade **AI Forward Deployed Engineer (FDE) Copilot** for Quantitative Credit Risk. This project bridges the gap between complex IFRS 9 Stress-Testing models and business users by combining a **54-million-row loan-level dataset** with a local **Llama 3 Agent** capable of querying the data, running macro stress tests, and explaining credit policy via Retrieval-Augmented Generation (RAG).

![Python](https://img.shields.io/badge/Python-3.13-blue.svg)
![LangChain](https://img.shields.io/badge/LangChain-0.2-orange.svg)
![Ollama](https://img.shields.io/badge/Ollama-Llama%203-black.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30-red.svg)

## The AI FDE in Action

The screenshot below shows the AI Copilot performing live calculations on a 5.4M-row dataset:
1. **Root-Cause Analysis:** Explaining *why* the 2008 vintage has high ECL by querying average FICO and LTV.
2. **Deep Data Lookup:** Finding a specific loan (`F08Q10000071`) and pulling its exact ECL and Stage.
3. **Policy RAG:** Citing the exact policy for Stage 2 staging.
4. **Macro Stress:** Dynamically recalculating ECL under an HPI shock.

<img src="ai_fde_chat_output.png" width="100%">
*Figure 1: The AI FDE Copilot executing Python tools and retrieving policy context in real-time.*

## Portfolio Monitoring Dashboard

The executive dashboard below provides a holistic view of the portfolio. It includes the cumulative default curve by loan age (highlighting the reference vs. current portfolio), coverage ratios by stage, staging distribution, ECL contribution by vintage, and automated monitoring alerts.

<img src="11_monitoring_dashboard.png" width="100%">
*Figure 2: 6-panel IFRS 9 Portfolio Monitoring Dashboard.*

## Model Diagnostics & Validation

The AI Agent is powered by an underlying Logistic Regression IFRS 9 engine built on 54 million loan-month observations (2006–2023). 

*   **Out-of-Time AUC:** **0.8171** (Discrimination)
*   **Out-of-Time Gini:** **0.6342** (Elite for mortgage models)
*   **Portfolio Exposure:** R 1.03 Trillion
*   **Total ECL:** R 4.2 Billion (Coverage Ratio: 0.41%)

### 1. Default Rate by Origination Vintage
The portfolio captures the macroeconomic cycles perfectly, showing the severe impact of the 2008 Global Financial Crisis and the 2020 COVID shock.

<img src="default_rate_vintage.png" width="100%">
*Figure 3: Default rate by origination vintage.*

### 2. Delinquency Transition Matrix
To validate the credit mechanics, we analyzed the roll rates. The matrix shows the high probability of curing from 30 DPD (50.7% return to Current), compared to the "stickiness" of 90+ DPD (72.1% remain in default).

<img src="transition_matrix.png" width="80%">
*Figure 4: 1-month delinquency transition matrix.*

### 3. Model Discrimination (ROC Curve)
The champion model demonstrates strong rank-ordering capabilities across both the Train and Test datasets.

<img src="roc_curve.png" width="80%">
*Figure 5: ROC Curve for the 12-month PD Champion model.*

### 4. IFRS 9 Staging by Vintage
The engine correctly front-loads provisions by shifting nearly 95% of the 2006-2008 vintage balance into Stage 2 to anticipate the subprime crash. In benign years (2012, 2020), 97%+ of the portfolio sits safely in Stage 1.

<img src="08_staging_by_vintage.png" width="100%">
*Figure 6: IFRS 9 Staging migration across the GFC and COVID-19 shocks.*

### 5. Year-Level Coverage & ECL
By isolating crisis years, we see how the ECL engine reacts differently to a structural credit crash (2008) vs. a temporary liquidity shock (2020). The 2008 vintage requires a massive 16.5% coverage ratio in Stage 2, while the 2020 vintage only requires 9.4%.

<img src="10b_year_comparison.png" width="100%">
*Figure 7: Staging distribution and Coverage Ratios (ECL / EAD) for key economic vintages.*

## Technical Architecture

This is not a simple chatbot. It is a **ReAct Agent** (Reason + Act) that can execute code.

*   **The Brain:** `llama3.1` (running locally via Ollama for enterprise data privacy).
*   **The Agent Framework:** `LangGraph` (to route prompts to the correct Python tools).
*   **The Memory/RAG:** `ChromaDB` + `nomic-embed-text` (to read and search the `Freddie_Mac_Policy.txt`).
*   **The Tools:** Custom Python functions (`@tool`) that allow the AI to calculate portfolio KPIs, filter specific loans, and run stress tests on the live 5.4M row CSV.
*   **The Frontend:** `Streamlit` for a real-time, interactive chat interface and KPI dashboard.

## Model Validation
This project was developed to **SR 11-7** standards. All staging rules, calibrations, and transition matrices are documented in the validation report.

📄 **[Click here to read the full Model Validation Report](freddie_mac_validation_v1.md)**

## How to Run Locally

1. **Clone the repo:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/Freddie-Mac-IFRS9-AI-FDE-Copilot.git
   cd Freddie-Mac-IFRS9-AI-FDE-Copilot
