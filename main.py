"""Simple sales dashboard built with Streamlit.

Run with:
    streamlit run main.py
"""

import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Sales Dashboard", page_icon="📊", layout="wide")


@st.cache_data
def load_sales_data() -> pd.DataFrame:
    """Generate fake sales data for the demo."""
    rng = np.random.default_rng(seed=42)
    dates = pd.date_range("2026-01-01", "2026-06-30", freq="D")
    regions = ["North", "South", "East", "West"]
    products = ["Laptop", "Phone", "Tablet", "Monitor"]

    row_count = len(dates) * 3
    return pd.DataFrame(
        {
            "date": rng.choice(dates, size=row_count),
            "region": rng.choice(regions, size=row_count),
            "product": rng.choice(products, size=row_count),
            "units": rng.integers(1, 20, size=row_count),
            "unit_price": rng.choice([300, 500, 800, 1200], size=row_count),
        }
    ).assign(revenue=lambda df: df["units"] * df["unit_price"])


sales = load_sales_data()

# Sidebar filters
st.sidebar.header("Filters")
selected_regions = st.sidebar.multiselect(
    "Region", sorted(sales["region"].unique()), default=sorted(sales["region"].unique())
)
selected_products = st.sidebar.multiselect(
    "Product", sorted(sales["product"].unique()), default=sorted(sales["product"].unique())
)

filtered_sales = sales[
    sales["region"].isin(selected_regions) & sales["product"].isin(selected_products)
]

st.title("📊 Sales Dashboard")

if filtered_sales.empty:
    st.warning("No data for the selected filters.")
    st.stop()

# KPIs
total_revenue = filtered_sales["revenue"].sum()
total_units = filtered_sales["units"].sum()
order_count = len(filtered_sales)

kpi_revenue, kpi_units, kpi_orders = st.columns(3)
kpi_revenue.metric("Total revenue", f"${total_revenue:,.0f}")
kpi_units.metric("Units sold", f"{total_units:,}")
kpi_orders.metric("Orders", f"{order_count:,}")

st.divider()

# Charts
chart_left, chart_right = st.columns(2)

with chart_left:
    st.subheader("Monthly revenue")
    monthly_revenue = (
        filtered_sales.set_index("date").resample("MS")["revenue"].sum()
    )
    st.line_chart(monthly_revenue)

with chart_right:
    st.subheader("Revenue by region")
    revenue_by_region = filtered_sales.groupby("region")["revenue"].sum()
    st.bar_chart(revenue_by_region)

st.subheader("Units by product")
st.bar_chart(filtered_sales.groupby("product")["units"].sum())

with st.expander("Show raw data"):
    st.dataframe(filtered_sales.sort_values("date"), use_container_width=True)
