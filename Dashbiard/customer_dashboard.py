from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


DATA_FILE = Path(__file__).resolve().parent / "customer_segments.csv"

st.set_page_config(
    page_title="Customer Segmentation Dashboard",
    page_icon="👥",
    layout="wide",
)


@st.cache_data
def load_data():
    data = pd.read_csv(DATA_FILE)
    data["total_sales"] = pd.to_numeric(data["total_sales"])
    data["total_profit"] = pd.to_numeric(data["total_profit"])
    data["order_count"] = pd.to_numeric(data["order_count"])
    data["avg_discount"] = pd.to_numeric(data["avg_discount"])
    return data


data = load_data()

st.title("Customer Segmentation Dashboard")
st.caption("Customer groups based on sales, profit, order frequency, and discount behavior")

segments = sorted(data["cluster_label"].unique())
selected_segments = st.multiselect("Filter customer segments", segments, default=segments)
filtered = data[data["cluster_label"].isin(selected_segments)]

if filtered.empty:
    st.warning("Select at least one customer segment.")
    st.stop()

total_customers = len(filtered)
total_sales = filtered["total_sales"].sum()
total_profit = filtered["total_profit"].sum()
avg_orders = filtered["order_count"].mean()

metric_columns = st.columns(4)
metric_columns[0].metric("Customers", f"{total_customers:,}")
metric_columns[1].metric("Total Sales", f"${total_sales:,.0f}")
metric_columns[2].metric("Total Profit", f"${total_profit:,.0f}")
metric_columns[3].metric("Average Orders", f"{avg_orders:.1f}")

summary = (
    filtered.groupby("cluster_label", as_index=False)
    .agg(
        customers=("Customer ID", "count"),
        sales=("total_sales", "sum"),
        profit=("total_profit", "sum"),
        orders=("order_count", "sum"),
    )
)

left, right = st.columns(2)
with left:
    st.subheader("Customers by Segment")
    segment_counts = filtered["cluster_label"].value_counts().rename_axis("segment").reset_index(name="customers")
    st.plotly_chart(
        px.pie(segment_counts, names="segment", values="customers", hole=0.45),
        width="stretch",
    )
with right:
    st.subheader("Sales and Profit by Segment")
    chart_data = summary.melt("cluster_label", value_vars=["sales", "profit"], var_name="metric", value_name="amount")
    st.plotly_chart(
        px.bar(chart_data, x="cluster_label", y="amount", color="metric", barmode="group"),
        width="stretch",
    )

st.subheader("Segment Profiles")
profile = (
    filtered.groupby("cluster_label", as_index=False)
    .agg(
        customers=("Customer ID", "count"),
        avg_sales=("total_sales", "mean"),
        avg_profit=("total_profit", "mean"),
        avg_orders=("order_count", "mean"),
        avg_discount=("avg_discount", "mean"),
    )
)
st.dataframe(
    profile.style.format(
        {
            "avg_sales": "${:,.2f}",
            "avg_profit": "${:,.2f}",
            "avg_orders": "{:,.1f}",
            "avg_discount": "{:.1%}",
        }
    ),
    width="stretch",
    hide_index=True,
)

st.subheader("Customer Details")
search = st.text_input("Search by customer name or ID")
customer_view = filtered.copy()
if search:
    search_value = search.lower()
    customer_view = customer_view[
        customer_view["customer_name"].str.lower().str.contains(search_value, na=False)
        | customer_view["Customer ID"].str.lower().str.contains(search_value, na=False)
    ]
st.dataframe(
    customer_view.sort_values("total_profit", ascending=False),
    width="stretch",
    hide_index=True,
)
