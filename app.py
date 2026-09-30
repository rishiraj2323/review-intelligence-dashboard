import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Review Intelligence Dashboard", layout="wide")

st.title("⌚ Smartwatch Review Intelligence Dashboard")
st.write("Rating vs Sentiment mismatch analysis across Flipkart smartwatch reviews")

# Data loading — precomputed CSV, no live database connection
# (this is what raw_reviews JOIN processed_reviews used to give us via Postgres,
# now saved as a static snapshot so the deployed app never needs a live DB)
@st.cache_data
def load_data():
    df = pd.read_csv("dashboard_data.csv")
    return df

df = load_data()

st.metric("Total Reviews Analyzed", len(df))