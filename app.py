%%writefile app.py

import os
import streamlit as st
import pandas as pd
import plotly.express as px
from groq import Groq


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="SALESVISTA",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# CUSTOM UI
# =========================================================

st.markdown("""
<style>

    .stApp {
        background: #f7f8fc;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f0ecff 0%, #eef7ff 55%, #edfff8 100%);
        border-right: 1px solid #e4e7f0;
    }

    .main-title {
        font-size: 42px;
        font-weight: 800;
        color: #4936a8;
        margin-bottom: 0;
    }

    .subtitle {
        color: #687085;
        font-size: 16px;
        margin-top: 2px;
        margin-bottom: 25px;
    }

    .section-title {
        font-size: 24px;
        font-weight: 750;
        color: #25283a;
        margin-top: 25px;
        margin-bottom: 12px;
    }

    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid #e8eaf2;
        border-radius: 18px;
        padding: 18px;
        box-shadow: 0 5px 18px rgba(56, 61, 90, 0.06);
    }

    div[data-testid="stMetricLabel"] {
        color: #687085;
        font-weight: 600;
    }

    div[data-testid="stMetricValue"] {
        color: #302d63;
        font-weight: 800;
    }

    .info-card {
        background: white;
        border-radius: 18px;
        border: 1px solid #e8eaf2;
        padding: 20px;
        box-shadow: 0 5px 18px rgba(56, 61, 90, 0.05);
    }

    .ai-card {
        background: linear-gradient(135deg, #f0ecff, #eef7ff);
        border: 1px solid #ddd6ff;
        border-radius: 18px;
        padding: 22px;
        margin-top: 10px;
    }

    .footer {
        text-align: center;
        color: #85899a;
        font-size: 13px;
        padding: 30px 0 10px 0;
    }

</style>
""", unsafe_allow_html=True)


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def find_column(columns, names):
    """Find a column using common sales-dataset names."""
    normalized = {
        str(c).lower().strip().replace("_", " ").replace("-", " "): c
        for c in columns
    }

    for name in names:
        key = name.lower().strip().replace("_", " ").replace("-", " ")
        if key in normalized:
            return normalized[key]

    for c in columns:
        clean = str(c).lower().strip().replace("_", " ").replace("-", " ")
        for name in names:
            target = name.lower().strip().replace("_", " ").replace("-", " ")
            if target in clean or clean in target:
                return c

    return None


def money(value):
    if pd.isna(value):
        return "0"
    return f"{value:,.0f}"


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown(
        "<h2 style='color:#4936a8; margin-bottom:0;'>SALESVISTA</h2>",
        unsafe_allow_html=True
    )

    st.caption("Smart Sales Analytics")

    st.divider()

    uploaded_file = st.file_uploader(
        "Upload Sales Dataset",
        type=["csv", "xlsx"]
    )

    st.divider()

    st.markdown("### Dashboard")
    st.caption("Interactive sales & business analysis")

    st.divider()

    st.markdown(
        "<p style='text-align:center;color:#777;'>Created by Areeba</p>",
        unsafe_allow_html=True
    )


# =========================================================
# HEADER
# =========================================================

st.markdown(
    "<div class='main-title'>SALESVISTA</div>",
    unsafe_allow_html=True
)

st.markdown(
    "<div class='subtitle'>Smart Sales Data Analysis Dashboard</div>",
    unsafe_allow_html=True
)


# =========================================================
# NO DATA
# =========================================================

if uploaded_file is None:

    st.markdown("""
    <div class="info-card">
        <h3 style="color:#4936a8;">Welcome to SALESVISTA</h3>
        <p style="color:#687085;">
        Upload your sales dataset from the sidebar to explore
        sales performance, profit, customers, products and trends.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.stop()


# =========================================================
# LOAD DATA
# =========================================================

try:

    if uploaded_file.name.lower().endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

except Exception as e:

    st.error(f"Unable to read the dataset: {e}")
    st.stop()


if df.empty:
    st.warning("The uploaded dataset is empty.")
    st.stop()


st.success(
    f"Dataset loaded successfully — {len(df):,} records and {len(df.columns):,} columns."
)


# =========================================================
# COLUMN DETECTION
# =========================================================

sales_col = find_column(
    df.columns,
    ["sales", "revenue", "amount", "total sales", "sales amount"]
)

profit_col = find_column(
    df.columns,
    ["profit", "net profit", "gross profit"]
)

order_col = find_column(
    df.columns,
    ["order id", "order", "order number", "order no"]
)

customer_col = find_column(
    df.columns,
    ["customer id", "customer", "customer name", "client", "client name"]
)

product_col = find_column(
    df.columns,
    ["product", "product name", "item", "item name"]
)

category_col = find_column(
    df.columns,
    ["category", "product category", "segment"]
)

region_col = find_column(
    df.columns,
    ["region", "area", "state", "city", "territory"]
)

date_col = find_column(
    df.columns,
    ["date", "order date", "sales date", "transaction date"]
)


# =========================================================
# CONVERT NUMERIC COLUMNS
# =========================================================

for col in df.columns:

    if df[col].dtype == "object":

        converted = pd.to_numeric(
            df[col].astype(str).str.replace(",", "", regex=False),
            errors="coerce"
        )

        if converted.notna().sum() > len(df) * 0.7:
            df[col] = converted


# Re-detect after conversion
numeric_columns = df.select_dtypes(include="number").columns.tolist()


# =========================================================
# KPI CALCULATIONS
# =========================================================

if sales_col:
    total_sales = pd.to_numeric(
        df[sales_col],
        errors="coerce"
    ).fillna(0).sum()
else:
    total_sales = 0


if profit_col:
    total_profit = pd.to_numeric(
        df[profit_col],
        errors="coerce"
    ).fillna(0).sum()
else:
    total_profit = 0


if order_col:
    total_orders = df[order_col].nunique()
else:
    total_orders = len(df)


if customer_col:
    total_customers = df[customer_col].nunique()
else:
    total_customers = 0


# =========================================================
# KPI CARDS
# =========================================================

st.markdown(
    "<div class='section-title'>Business Overview</div>",
    unsafe_allow_html=True
)

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric(
        "Total Sales",
        money(total_sales)
    )

with c2:
    st.metric(
        "Total Profit",
        money(total_profit)
    )

with c3:
    st.metric(
        "Total Orders",
        f"{total_orders:,}"
    )

with c4:
    st.metric(
        "Customers",
        f"{total_customers:,}"
    )


# =========================================================
# SIDEBAR FILTERS
# =========================================================

st.sidebar.divider()
st.sidebar.markdown("### Filters")

filtered_df = df.copy()


if region_col:

    regions = sorted(
        df[region_col].dropna().astype(str).unique().tolist()
    )

    selected_regions = st.sidebar.multiselect(
        "Region",
        regions,
        default=regions
    )

    if selected_regions:
        filtered_df = filtered_df[
            filtered_df[region_col].astype(str).isin(selected_regions)
        ]


if category_col:

    categories = sorted(
        df[category_col].dropna().astype(str).unique().tolist()
    )

    selected_categories = st.sidebar.multiselect(
        "Category",
        categories,
        default=categories
    )

    if selected_categories:
        filtered_df = filtered_df[
            filtered_df[category_col].astype(str).isin(selected_categories)
        ]


if product_col:

    products = sorted(
        df[product_col].dropna().astype(str).unique().tolist()
    )

    if len(products) <= 100:

        selected_products = st
