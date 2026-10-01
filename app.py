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
    return pd.read_csv("dashboard_data.csv")

df = load_data()

st.metric("Total Reviews Analyzed", len(df))

# Sidebar filters
st.sidebar.header("🔍 Filters")

brands = sorted(df["brand"].unique())
selected_brands = st.sidebar.multiselect("Select Brand(s)", brands, default=brands)

filtered_df = df[df["brand"].isin(selected_brands)]

products = sorted(filtered_df["product_name"].unique())
selected_products = st.sidebar.multiselect("Select Product(s)", products, default=products)

filtered_df = filtered_df[filtered_df["product_name"].isin(selected_products)]

st.metric("Filtered Reviews", len(filtered_df))

st.divider()
st.subheader("📊 Brand-wise Rating vs Sentiment")

brand_summary = filtered_df.groupby("brand").agg(
    avg_rating=("rating", "mean"),
    pct_positive=("sentiment_label", lambda x: (x == "POSITIVE").mean() * 100),
    review_count=("review_id", "count")
).reset_index()

fig1 = px.bar(
    brand_summary, x="brand", y="pct_positive",
    title="Percentage of Positive Reviews by Brand (Sentiment Model)",
    labels={"pct_positive": "% Positive Reviews", "brand": "Brand"},
    color="pct_positive", color_continuous_scale="RdYlGn"
)
st.plotly_chart(fig1, use_container_width=True)

fig1b = px.bar(
    brand_summary, x="brand", y="avg_rating",
    title="Average Star Rating by Brand",
    labels={"avg_rating": "Average Rating (1-5)", "brand": "Brand"}
)
st.plotly_chart(fig1b, use_container_width=True)

st.divider()
st.subheader("⚠️ Rating vs Sentiment Mismatches")

mismatch_summary = filtered_df.groupby("brand").agg(
    total_reviews=("review_id", "count"),
    mismatch_count=("is_mismatch", "sum")
).reset_index()
mismatch_summary["mismatch_pct"] = (mismatch_summary["mismatch_count"] / mismatch_summary["total_reviews"] * 100).round(1)

fig2 = px.bar(
    mismatch_summary, x="brand", y="mismatch_pct",
    title="% of Reviews with Rating-Sentiment Mismatch by Brand",
    labels={"mismatch_pct": "% Mismatch", "brand": "Brand"},
    color="mismatch_pct", color_continuous_scale="Reds"
)
st.plotly_chart(fig2, use_container_width=True)

st.write("Sample mismatched reviews (high-confidence only, score > 0.90):")
mismatch_df = filtered_df[
    (filtered_df["is_mismatch"] == True) & (filtered_df["sentiment_score"] > 0.90)
][["product_name", "brand", "rating", "sentiment_label", "sentiment_score", "review_text"]]
st.dataframe(mismatch_df, use_container_width=True)

st.divider()
st.subheader("🔎 Search Reviews")

search_term = st.text_input("Search by keyword (e.g. 'battery', 'display', 'strap')")

if search_term:
    search_results = filtered_df[
        filtered_df["review_text"].str.contains(search_term, case=False, na=False)
    ][["product_name", "brand", "rating", "sentiment_label", "review_text"]]
    st.write(f"Found {len(search_results)} reviews containing '{search_term}'")
    st.dataframe(search_results, use_container_width=True)

st.warning(
    "⚠️ Manual spot-check: several high-confidence 'NEGATIVE' labels are on short, "
    "positive-sounding text (e.g., 'Gud purchase', 'Very gud product'). This points to a real "
    "limitation: DistilBERT (trained on English movie reviews) can misclassify short, "
    "Hinglish-influenced reviews. This is documented as a limitation, not hidden."
)