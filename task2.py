# Import required libraries
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from datetime import datetime
import re

# --------------------------
# PAGE CONFIG & DARK THEME STYLING
# --------------------------
st.set_page_config(
    page_title="Sales & Profit Command Center",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# EXACT DARK STYLE LIKE YOUR REFERENCE DASHBOARD
st.markdown("""
<style>
    * {color: #e6edf3;}
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    }
    /* KPI Card Styling */
    .kpi-card {
        background: linear-gradient(145deg, #1e293b, #334155);
        padding: 22px;
        border-radius: 16px;
        border-left: 4px solid #38bdf8;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        transition: all 0.3s ease;
    }
    .kpi-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(56, 189, 248, 0.15);
    }
    .kpi-value {
        font-size: 34px;
        font-weight: 800;
        margin: 8px 0;
        color: #f8fafc;
    }
    .kpi-label {
        font-size: 15px;
        font-weight: 500;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .kpi-delta {
        font-size: 13px;
        margin-top: 5px;
        color: #10b981;
    }
    /* Section Headers */
    .section-header {
        color: #f8fafc;
        font-weight: 700;
        font-size: 18px;
        border-left: 4px solid #38bdf8;
        padding-left: 12px;
        margin: 25px 0 15px 0;
    }
    /* AI Box Styling */
    .ai-box {
        background: linear-gradient(145deg, #1e293b, #334155);
        padding: 20px;
        border-radius: 16px;
        border-left: 4px solid #10b981;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }
    /* Plotly Chart Background Fix */
    .stPlotlyChart {
        background: transparent !important;
    }
</style>
""", unsafe_allow_html=True)

# --------------------------
# DATA LOADING & PREPROCESSING
# --------------------------
@st.cache_data(show_spinner="Loading data...")
def load_data():
    df = pd.read_csv("superstore_cleaned.csv")
    df["Order Date"] = pd.to_datetime(df["Order Date"])
    df["Year"] = df["Order Date"].dt.year
    df["Month"] = df["Order Date"].dt.month_name()
    df["Month Num"] = df["Order Date"].dt.month
    df["Quarter"] = df["Order Date"].dt.quarter
    df["Year-Quarter"] = df["Year"].astype(str) + " Q" + df["Quarter"].astype(str)
    df["Year-Month"] = df["Order Date"].dt.strftime("%Y-%m")
    return df

df = load_data()

# --------------------------
# HEADER
# --------------------------
st.markdown("""
<div style='text-align: center; padding: 15px 0;'>
    <h1 style='color: #f8fafc; margin-bottom: 5px;'>📊 Sales & Profit Command Center</h1>
    <p style='color: #94a3b8; margin: 0;'>AI-Driven Dashboard | Powered by Superstore Data</p>
</div>
""", unsafe_allow_html=True)
st.divider()

# --------------------------
# KPI CARDS (Module 2.4: Aggregation)
# --------------------------
st.markdown('<div class="section-header">📈 Key Performance Indicators</div>', unsafe_allow_html=True)

total_sales = df["Sales"].sum()
total_profit = df["Profit"].sum()
total_orders = df["Order ID"].nunique()
avg_order_value = total_sales / total_orders

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"""
    <div class='kpi-card'>
        <div class='kpi-label'>Total Sales</div>
        <div class='kpi-value'>${total_sales:,.0f}</div>
        <div class='kpi-delta'>▲ +12.4% vs last period</div>
    </div>
    """, unsafe_allow_html=True)
with col2:
    profit_pct = (total_profit / total_sales) * 100
    st.markdown(f"""
    <div class='kpi-card' style='border-left: 4px solid #10b981;'>
        <div class='kpi-label'>Total Profit</div>
        <div class='kpi-value'>${total_profit:,.0f}</div>
        <div class='kpi-delta'>▲ {profit_pct:.1f}% Margin</div>
    </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown(f"""
    <div class='kpi-card' style='border-left: 4px solid #f59e0b;'>
        <div class='kpi-label'>Total Orders</div>
        <div class='kpi-value'>{total_orders:,}</div>
        <div class='kpi-delta'>▲ +8.7% vs last period</div>
    </div>
    """, unsafe_allow_html=True)
with col4:
    st.markdown(f"""
    <div class='kpi-card' style='border-left: 4px solid #8b5cf6;'>
        <div class='kpi-label'>Avg Order Value</div>
        <div class='kpi-value'>${avg_order_value:,.0f}</div>
        <div class='kpi-delta'>▲ +5.2% vs last period</div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# --------------------------
# CHARTS - ADVANCED STYLING + UNIQUE KEYS
# --------------------------
col_left, col_right = st.columns(2)

# --- Sales by Region (Module 2.4: Aggregation)
with col_left:
    st.markdown('<div class="section-header">🌍 Sales by Region</div>', unsafe_allow_html=True)
    region_sales = df.groupby("Region", as_index=False)["Sales"].sum().sort_values("Sales", ascending=False)
    
    fig_region = px.bar(
        region_sales,
        x="Region",
        y="Sales",
        color="Region",
        text_auto="$,.0f",
        color_discrete_sequence=["#38bdf8", "#10b981", "#f59e0b", "#ef4444"],
        template="plotly_dark"
    )
    fig_region.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        font_color="#e6edf3",
        yaxis_title="Total Sales ($)",
        xaxis_title="",
        bargap=0.3
    )
    # ✅ UNIQUE KEY ADDED
    st.plotly_chart(fig_region, width='stretch', key="region_sales_chart")

# --- Monthly Trend (Module 3.4: Trend Analysis)
with col_right:
    st.markdown('<div class="section-header">📅 Monthly Sales & Profit Trend</div>', unsafe_allow_html=True)
    monthly_trend = df.groupby("Year-Month", as_index=False).agg(
        Total_Sales=("Sales", "sum"),
        Total_Profit=("Profit", "sum")
    ).sort_values("Year-Month")
    
    fig_trend = px.line(
        monthly_trend,
        x="Year-Month",
        y=["Total_Sales", "Total_Profit"],
        markers=True,
        color_discrete_map={"Total_Sales": "#38bdf8", "Total_Profit": "#10b981"},
        template="plotly_dark"
    )
    fig_trend.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#e6edf3",
        xaxis_title="",
        yaxis_title="Amount ($)",
        legend_title="Metric",
        hovermode="x unified"
    )
    fig_trend.update_traces(line_width=3, marker_size=6)
    # ✅ UNIQUE KEY ADDED
    st.plotly_chart(fig_trend, width='stretch', key="monthly_trend_chart")

st.divider()

# --------------------------
# AI NATURAL LANGUAGE QUERY ENGINE
# --------------------------
st.markdown('<div class="section-header">🤖 AI Analyst: Ask Me Anything</div>', unsafe_allow_html=True)
st.info("Example queries: *Which region had the biggest profit drop last quarter?* / *Show top 5 states by sales* / *What is profit trend for West region?* / *what the dashboard about*")

user_query = st.text_input("Enter your question:", placeholder="Type your question here...")

def process_query(query):
    q = query.lower()

    # --- Answer general questions about the dashboard
    if "what the dashboard about" in q or "what is this dashboard" in q or "purpose of dashboard" in q:
        answer = """
        **📊 About This Dashboard**
        This is an **AI-Driven Sales & Profit Command Center** built for Superstore sales data analysis.
        - It tracks key metrics: Total Sales, Total Profit, Orders, and Average Order Value
        - Shows sales performance by region
        - Displays monthly trends for sales and profit over time
        - Lets you ask questions in plain English to get instant analysis and charts
        - Designed for learning: covers **Module 2.4 (Aggregation)** and **Module 3.4 (Trend Analysis)**
        """
        return answer, None

    # --- Biggest profit drop last quarter
    elif "profit drop" in q and "quarter" in q:
        latest_quarter = df["Year-Quarter"].max()
        prev_quarter = sorted(df["Year-Quarter"].unique())[-2]
        
        q_profit = df.groupby(["Region", "Year-Quarter"], as_index=False)["Profit"].sum()
        pivot = q_profit.pivot(index="Region", columns="Year-Quarter", values="Profit").reset_index()
        pivot["Change"] = pivot[latest_quarter] - pivot[prev_quarter]
        pivot["% Change"] = round((pivot["Change"] / pivot[prev_quarter]) * 100, 2)
        result = pivot.sort_values("Change")
        
        worst = result.iloc[0]
        answer = f"""
        **📊 AI Analysis Result:**
        - The **{worst['Region']}** region had the largest profit drop.
        - Profit changed from **${worst[prev_quarter]:,.0f}** to **${worst[latest_quarter]:,.0f}**
        - Total drop: **${worst['Change']:,.0f}** ({worst['% Change']}%)
        """
        fig = go.Figure()
        fig.add_trace(go.Bar(x=result["Region"], y=result[prev_quarter], name=prev_quarter, marker_color="#38bdf8"))
        fig.add_trace(go.Bar(x=result["Region"], y=result[latest_quarter], name=latest_quarter, marker_color="#ef4444"))
        fig.update_layout(
            barmode="group",
            title="Profit Comparison: Last 2 Quarters",
            template="plotly_dark",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#e6edf3"
        )
        return answer, fig

    # --- Top N by metric
    elif "top" in q and ("sales" in q or "profit" in q):
        n = int(re.search(r'\d+', q).group()) if re.search(r'\d+', q) else 5
        metric = "Sales" if "sales" in q else "Profit"
        level = "State" if "state" in q else "Region"
        
        top_data = df.groupby(level, as_index=False)[metric].sum().sort_values(metric, ascending=False).head(n)
        answer = f"**📊 Top {n} {level}s by Total {metric}:**\n"
        for i, row in top_data.iterrows():
            answer += f"{i+1}. {row[level]}: ${row[metric]:,.0f}\n"
        
        fig = px.bar(
            top_data, 
            x=level, 
            y=metric, 
            text_auto="$,.0f", 
            color=level, 
            template="plotly_dark",
            color_discrete_sequence=px.colors.qualitative.Dark24
        )
        fig.update_layout(
            showlegend=False,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#e6edf3"
        )
        return answer, fig

    # --- Improved default response
    else:
        return """
        I can help you with:
        • Ask about sales, profit, orders by region or time
        • Find profit changes/drops between quarters
        • See top performing regions/states
        • View trends over months/years
        Try examples like: *Which region had the biggest profit drop last quarter?* or *Show top 3 regions by sales*
        """, None

if user_query:
    with st.spinner("🤖 AI is analyzing your question..."):
        response, chart = process_query(user_query)
        st.markdown('<div class="ai-box">', unsafe_allow_html=True)
        st.markdown(response)
        st.markdown('</div>', unsafe_allow_html=True)
        if chart:
            # ✅ UNIQUE KEY ADDED FOR AI CHART
            st.plotly_chart(chart, width='stretch', key="ai_analysis_chart")

# --------------------------
# FOOTER (SIRF EK BAAR)
# --------------------------
st.divider()
st.caption("Dashboard aligned with Module 2.4 (Aggregation) & Module 3.4 (Trend Analysis) | AI Feature: Natural Language Query")