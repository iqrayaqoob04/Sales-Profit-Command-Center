from pathlib import Path
import html
import re

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from flask import Flask, request


ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "superstore_cleaned.csv"
app = Flask(__name__)


def load_data():
    data = pd.read_csv(DATA_FILE)
    data["Order Date"] = pd.to_datetime(data["Order Date"])
    data["Year"] = data["Order Date"].dt.year
    data["Quarter"] = data["Order Date"].dt.quarter
    data["Year-Quarter"] = data["Year"].astype(str) + " Q" + data["Quarter"].astype(str)
    data["Year-Month"] = data["Order Date"].dt.strftime("%Y-%m")
    return data


DATA = load_data()


def chart_html(figure):
    figure.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#e6edf3",
        margin=dict(l=40, r=20, t=55, b=45),
    )
    return figure.to_html(full_html=False, include_plotlyjs="cdn", config={"responsive": True})


def query_result(query):
    normalized = query.lower().strip()

    if any(phrase in normalized for phrase in ("what the dashboard about", "what is this dashboard", "purpose of dashboard")):
        return (
            "This dashboard analyzes Superstore sales data, including sales, profit, orders, regional performance, and monthly trends.",
            None,
        )

    if "profit drop" in normalized and "quarter" in normalized:
        quarters = sorted(DATA["Year-Quarter"].dropna().unique())
        if len(quarters) < 2:
            return "There are not enough quarters for a comparison.", None
        latest_quarter, previous_quarter = quarters[-1], quarters[-2]
        quarterly = DATA.groupby(["Region", "Year-Quarter"], as_index=False)["Profit"].sum()
        pivot = quarterly.pivot(index="Region", columns="Year-Quarter", values="Profit").fillna(0)
        pivot["Change"] = pivot[latest_quarter] - pivot[previous_quarter]
        result = pivot.sort_values("Change")
        worst = result.iloc[0]
        answer = (
            f"{worst.name} had the largest profit change: "
            f"${worst[previous_quarter]:,.0f} to ${worst[latest_quarter]:,.0f} "
            f"({worst['Change']:+,.0f})."
        )
        figure = go.Figure()
        figure.add_bar(x=result.index, y=result[previous_quarter], name=previous_quarter, marker_color="#38bdf8")
        figure.add_bar(x=result.index, y=result[latest_quarter], name=latest_quarter, marker_color="#ef4444")
        figure.update_layout(barmode="group", title="Profit Comparison: Last 2 Quarters")
        return answer, chart_html(figure)

    if "top" in normalized and ("sales" in normalized or "profit" in normalized):
        number_match = re.search(r"\d+", normalized)
        number = min(int(number_match.group()) if number_match else 5, 25)
        metric = "Sales" if "sales" in normalized else "Profit"
        level = "State" if "state" in normalized else "Region"
        top_data = DATA.groupby(level, as_index=False)[metric].sum().sort_values(metric, ascending=False).head(number)
        answer = "Top {} {}s by {}: {}".format(
            number,
            level,
            metric,
            ", ".join(f"{row[level]} (${row[metric]:,.0f})" for _, row in top_data.iterrows()),
        )
        figure = px.bar(top_data, x=level, y=metric, color=level, title=f"Top {number} {level}s by {metric}")
        return answer, chart_html(figure)

    return (
        "Try: 'What is this dashboard?', 'Show top 5 states by sales', or "
        "'Which region had the biggest profit drop last quarter?'",
        None,
    )


def page(query="", answer="", chart=""):
    sales = DATA["Sales"].sum()
    profit = DATA["Profit"].sum()
    orders = DATA["Order ID"].nunique()
    cards = "".join(
        f'<div class="card"><small>{label}</small><strong>{value}</strong></div>'
        for label, value in (
            ("Total Sales", f"${sales:,.0f}"),
            ("Total Profit", f"${profit:,.0f}"),
            ("Total Orders", f"{orders:,}"),
            ("Average Order Value", f"${sales / orders:,.0f}"),
        )
    )
    region = DATA.groupby("Region", as_index=False)["Sales"].sum().sort_values("Sales", ascending=False)
    region_figure = px.bar(region, x="Region", y="Sales", color="Region", title="Sales by Region")
    monthly = DATA.groupby("Year-Month", as_index=False).agg(Total_Sales=("Sales", "sum"), Total_Profit=("Profit", "sum"))
    monthly_figure = px.line(monthly.sort_values("Year-Month"), x="Year-Month", y=["Total_Sales", "Total_Profit"], markers=True, title="Monthly Sales and Profit")
    chart_blocks = chart_html(region_figure) + chart_html(monthly_figure)
    result = ""
    if answer:
        result = f'<section class="result"><b>Analyst result</b><p>{html.escape(answer)}</p>{chart}</section>'
    return f"""<!doctype html>
<html><head><meta name="viewport" content="width=device-width, initial-scale=1"><title>Sales & Profit Command Center</title>
<style>body{{margin:0;background:linear-gradient(135deg,#0f172a,#1e293b);color:#e6edf3;font:16px system-ui,sans-serif}}main{{max-width:1200px;margin:auto;padding:28px 18px}}h1{{font-size:clamp(2rem,5vw,3.5rem);margin:0 0 8px}}.muted,small{{color:#94a3b8}}.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:14px;margin:28px 0}}.card,.result{{background:#1e293b;border:1px solid #334155;border-radius:12px;padding:20px}}.card strong{{display:block;font-size:2rem;margin-top:8px;color:#f8fafc}}.charts{{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:18px}}.chart{{background:#172033;border-radius:12px;padding:8px;min-width:0}}form{{display:flex;gap:10px;margin:28px 0 14px}}input{{flex:1;padding:14px;border:1px solid #475569;border-radius:8px;background:#0f172a;color:#fff;font-size:1rem}}button{{padding:0 20px;border:0;border-radius:8px;background:#38bdf8;color:#082f49;font-weight:700;cursor:pointer}}@media(max-width:600px){{form{{flex-direction:column}}button{{padding:14px}}}}</style></head>
<body><main><h1>Sales & Profit Command Center</h1><p class="muted">Superstore performance dashboard</p><div class="cards">{cards}</div>
<form method="get"><input name="q" value="{html.escape(query)}" placeholder="Ask about sales or profit..."><button type="submit">Ask analyst</button></form>{result}
<div class="charts"><div class="chart">{chart_blocks}</div></div></main></body></html>"""


@app.get("/")
def home():
    query = request.args.get("q", "")
    answer, chart = query_result(query) if query else ("", "")
    return page(query, answer, chart or "")


if __name__ == "__main__":
    app.run(debug=True)