import streamlit as st
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

# --- 1. SETUP & LOAD FULL PRODUCTION DATA ---
BASE_DIR = r"C:\CreditRiskCourse\data\ai_ready"
DATA_PATH = os.path.join(BASE_DIR, "Freddie_Mac_IFRS9_Final.csv")
POLICY_PATH = "Freddie_Mac_Policy.txt" # Ensure this file is in the same folder

@st.cache_data
def load_full_portfolio():
    # Load the entire dataset (5.4M rows)
    df = pd.read_csv(DATA_PATH)
    return df

df_full = load_full_portfolio()

# --- 2. DEFINE THE AI TOOLS (Live Calculation) ---

@tool
def get_portfolio_kpis() -> str:
    """Returns the current total balance, total ECL, and coverage ratio of the entire Freddie Mac portfolio."""
    total_bal = df_full['EAD'].sum()
    total_ecl = df_full['ECL'].sum()
    cov = (total_ecl / total_bal) * 100
    return f"Total Portfolio EAD: R{total_bal:,.2f} | Total ECL: R{total_ecl:,.2f} | Coverage Ratio: {cov:.2f}%"

@tool
def analyze_vintage(vintage_year: int) -> str:
    """Calculates the ECL, average PD, average FICO, average LTV, and staging distribution for a specific vintage year (e.g., 2008, 2012, 2020)."""
    vint_df = df_full[df_full['Vintage_Year'] == vintage_year]
    if vint_df.empty:
        return f"No data found for vintage {vintage_year}."
    
    total_ecl = vint_df['ECL'].sum()
    avg_pd = vint_df['PD_12M'].mean()
    avg_fico = vint_df['CLASSIC FICO'].mean()
    avg_ltv = vint_df['ORIGINAL LOAN-TO-VALUE (LTV)'].mean()
    
    # Calculate stage distribution
    stage_bal = vint_df.groupby('IFRS9_Stage')['EAD'].sum()
    total_bal = stage_bal.sum()
    stage_pct = (stage_bal / total_bal * 100).round(2)
    
    return (f"Vintage {vintage_year} Analysis:\n"
            f"- Total ECL: R{total_ecl:,.2f}\n"
            f"- Average 12M PD: {avg_pd:.2%}\n"
            f"- Average FICO: {avg_fico:.0f}\n"
            f"- Average LTV: {avg_ltv:.2f}%\n"
            f"- Stage Distribution: Stage 1 = {stage_pct.get('Stage 1', 0)}%, "
            f"Stage 2 = {stage_pct.get('Stage 2', 0)}%, Stage 3 = {stage_pct.get('Stage 3', 0)}%")

@tool
def analyze_specific_loan(loan_id: str) -> str:
    """Returns the IFRS 9 stage, EAD, ECL, FICO, and LTV for a specific Loan ID."""
    loan = df_full[df_full['LOAN IDENTIFIER'] == loan_id]
    if loan.empty:
        return f"Loan {loan_id} not found in the database."
    
    latest = loan.iloc[-1]
    return (f"Loan {loan_id}: Stage={latest['IFRS9_Stage']}, EAD=R{latest['EAD']:,.2f}, "
            f"PD_12M={latest['PD_12M']:.2%}, ECL=R{latest['ECL']:,.2f}, "
            f"FICO={latest['CLASSIC FICO']}, LTV={latest['ORIGINAL LOAN-TO-VALUE (LTV)']}%")

@tool
def calculate_macro_stress_test(hpi_drop_pct: float) -> str:
    """Calculates the impact on Total ECL if HPI drops by a specific percentage (applying Policy 2.1)."""
    multiplier = 1.5 if hpi_drop_pct < -5.0 else 1.0
    base_ecl = df_full['ECL'].sum()
    stressed_ecl = base_ecl * multiplier
    
    return (f"If HPI drops by {abs(hpi_drop_pct)}%, the LGD increases. "
            f"Total Portfolio ECL would rise from R{base_ecl:,.2f} to R{stressed_ecl:,.2f}.")

@tool
def search_freddie_mac_policy(query: str) -> str:
    """Searches the Freddie Mac IFRS 9 Stress-Testing Policy for rules."""
    loader = TextLoader(POLICY_PATH)
    docs = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    splits = text_splitter.split_documents(docs)
    
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)
    
    results = vectorstore.similarity_search(query, k=1)
    return results[0].page_content if results else "Policy not found."

# --- 3. SETUP AI AGENT ---
@st.cache_resource
def setup_agent():
    llm = ChatOllama(model="llama3.1", temperature=0)
    tools = [get_portfolio_kpis, analyze_vintage, analyze_specific_loan, calculate_macro_stress_test, search_freddie_mac_policy]
    return create_react_agent(llm, tools)

agent = setup_agent()

# --- 4. STREAMLIT UI ---
st.set_page_config(page_title="Freddie Mac AI FDE", layout="wide")
st.title("🏦 Freddie Mac IFRS 9 FDE Copilot")
st.markdown("Ask questions about the full 5.4M row portfolio, specific loans, or policy rules. The AI calculates the answers live.")

total_bal = df_full['EAD'].sum()
total_ecl = df_full['ECL'].sum()

col1, col2, col3 = st.columns(3)
col1.metric("Total Portfolio EAD", f"R {total_bal/1e9:,.2f} Bn")
col2.metric("Total Portfolio ECL", f"R {total_ecl/1e6:,.2f} Mn")
col3.metric("Coverage Ratio", f"{(total_ecl/total_bal)*100:.2f}%")

st.divider()

# --- 5. AI COPILOT CHAT ---
st.subheader("🤖 Ask the FDE Copilot")
st.markdown("*Examples: 'Why is the ECL in 2008 so high?', 'What is the policy for Stage 2?', 'Show me the metrics for loan F08Q10000071', or 'What happens if HPI drops by 10%?'*")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask a question about the Freddie Mac portfolio..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.spinner("Agent is calculating from the full dataset..."):
        response = agent.invoke({"messages": [("user", prompt)]})
        final_answer = response["messages"][-1].content
        
    st.chat_message("assistant").markdown(final_answer)
    st.session_state.messages.append({"role": "assistant", "content": final_answer})