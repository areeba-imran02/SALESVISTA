
import streamlit as st
import pandas as pd
import plotly.express as px
from groq import Groq

st.set_page_config(
    page_title="SALESVISTA",
    page_icon="📊",
    layout="wide"
)

with st.sidebar:
    st.markdown("## SALESVISTA")
    st.caption("Smart Sales Analytics")
    st.divider()

    uploaded_file = st.file_uploader(
        "Upload Sales Dataset",
        type=["csv", "xlsx"]
    )

    st.divider()
    st.caption("Created by Areeba")

st.title("SALESVISTA")
st.caption("Smart Sales Data Analysis Dashboard")

if uploaded_file is not None:

    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.success("Dataset loaded successfully!")

    numeric_columns = df.select_dtypes(include="number").columns.tolist()

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total Records", f"{len(df):,}")
    c2.metric("Total Columns", f"{len(df.columns):,}")

    if numeric_columns:
        first_numeric = numeric_columns[0]

        c3.metric(
            f"Total {first_numeric}",
            f"{df[first_numeric].sum():,.0f}"
        )

        c4.metric(
            f"Average {first_numeric}",
            f"{df[first_numeric].mean():,.2f}"
        )
    else:
        c3.metric("Numeric Fields", "0")
        c4.metric("Data Status", "Ready")

    st.divider()

    st.subheader("Dataset Preview")
    st.dataframe(df, use_container_width=True)

else:
    st.info("Upload your CSV or Excel sales dataset from the sidebar to begin.")
