import streamlit as st
import pandas as pd
import numpy as np

# --- Function to calculate laundering probability ---
def calculate_laundering_probability(df):
    weights = {
        'route_distance': 0.20,
        'pricing_anomaly': 0.30,
        'tax_haven': 0.20,
        'doc_discrepancy': 0.10,
        'company_age': 0.20
    }

    tax_havens = ['Switzerland', 'Mauritius', 'Cayman Islands']
    route_distance_threshold = 3.0
    pricing_anomaly_threshold = 0.50
    company_age_threshold = 2

    df['ml_probability'] = 0.0

    # Route distance
    route_ratio = df['actual_distance'] / df['shortest_distance'].replace(0, np.nan)
    df.loc[route_ratio > route_distance_threshold, 'ml_probability'] += weights['route_distance']

    # Pricing anomaly
    price_difference = np.abs(df['unit_price'] - df['market_price']) / df['market_price'].replace(0, np.nan)
    df.loc[price_difference > pricing_anomaly_threshold, 'ml_probability'] += weights['pricing_anomaly']

    # Tax haven
    df.loc[df['origin_country'].isin(tax_havens), 'ml_probability'] += weights['tax_haven']

    # Document discrepancy
    df.loc[df['document_discrepancy'] == True, 'ml_probability'] += weights['doc_discrepancy']

    # Company age
    df.loc[df['company_age'] < company_age_threshold, 'ml_probability'] += weights['company_age']

    return df


# --- Streamlit App ---
st.title("💸 Money Laundering Risk Analyzer")

st.markdown("Enter transaction details below and analyze the **risk probability** of money laundering.")

# --- User Inputs ---
actual_dist = st.number_input("Actual Distance", min_value=0.0, value=8000.0, step=100.0)
shortest_dist = st.number_input("Shortest Distance", min_value=1.0, value=2000.0, step=100.0)
unit_price = st.number_input("Unit Price", min_value=0.0, value=1500.0, step=10.0)
market_price = st.number_input("Market Price", min_value=1.0, value=950.0, step=10.0)
origin_country = st.text_input("Origin Country", value="Panama")
company_age = st.number_input("Company Age (years)", min_value=0.0, value=1.5, step=0.1)
doc_discrepancy = st.checkbox("Document Discrepancy?")

# --- Analyze Button ---
if st.button("🔍 Analyze Transaction"):
    new_df = pd.DataFrame([{
        "transaction_id": "NEW_TXN",
        "actual_distance": actual_dist,
        "shortest_distance": shortest_dist,
        "unit_price": unit_price,
        "market_price": market_price,
        "origin_country": origin_country,
        "document_discrepancy": doc_discrepancy,
        "company_age": company_age
    }])

    result = calculate_laundering_probability(new_df)
    probability = result.loc[0, 'ml_probability']

    st.subheader("📊 Analysis Result")
    st.write(f"**Money Laundering Probability:** {probability:.2f} ({probability:.0%})")

    if probability >= 0.5:
        st.error("🚨 HIGH RISK: This transaction is suspicious.")
    elif probability >= 0.25:
        st.warning("⚠️ MODERATE RISK: Requires further review.")
    else:
        st.success("✅ LOW RISK: No major red flags detected.")

# --- Sample Batch Analysis ---
st.markdown("---")
st.subheader("📂 Sample Batch of Transactions")

data = {
    'transaction_id': [f'TXN{i:03}' for i in range(1, 11)],
    'actual_distance': [100, 5000, 250, 800, 12000, 300, 6000, 450, 1500, 9000],
    'shortest_distance': [90, 1500, 240, 750, 11000, 200, 5500, 400, 1400, 2500],
    'unit_price': [105, 200, 50, 80, 1500, 95, 25, 310, 55, 10.0],
    'market_price': [100, 190, 52, 85, 950, 98, 55, 300, 58, 9.5],
    'origin_country': ['USA', 'Cayman Islands', 'Germany', 'UK', 'Switzerland', 'Canada',
                       'Mauritius', 'Japan', 'China', 'Cayman Islands'],
    'document_discrepancy': [False, True, False, False, True, False, True, False, False, True],
    'company_age': [10, 1.2, 15, 8, 0.5, 25, 1.8, 30, 12, 0.2]
}
transactions_df = pd.DataFrame(data)
result_df = calculate_laundering_probability(transactions_df)
sorted_results = result_df.sort_values(by='ml_probability', ascending=False)

st.dataframe(sorted_results)



