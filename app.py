import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# =========================
# Load Excel File
# =========================
file_path = "moist_data.xlsx"  # make sure file is in same folder

# Get available sheet names
xls = pd.ExcelFile(file_path)
sheet_names = xls.sheet_names

# Try loading sheets dynamically
df_summary = pd.read_excel(file_path, sheet_name=[s for s in sheet_names if "Summary_excluding_outliers" in s.lower()][0])
df_farmer = pd.read_excel(file_path, sheet_name=[s for s in sheet_names if "Sheet1" in s.lower()][0])

# =========================
# Streamlit Dashboard
# =========================
st.set_page_config(page_title="Jubiliant Sugarcane Project", layout="wide")

st.title("🌾 Jubiliant Sugarcane Project Dashboard")

# Tabs
tab1, tab2 = st.tabs(["📊 Dashboard Summary", "👨‍🌾 Farmer Summary"])

# =========================
# TAB 1: Dashboard Summary
# =========================
with tab1:
    st.header("Village-wise Irrigation & Yield Summary")

    # Filters
    villages = df_summary["Village Name"].dropna().unique().tolist()
    selected_villages = st.multiselect("Select Village(s)", villages, default=[])

    if selected_villages:
        df_filtered = df_summary[df_summary["Village Name"].isin(selected_villages)]
    else:
        df_filtered = df_summary.copy()

    # KPIs
    total_devices = df_filtered["DeviceID"].nunique()
    total_farmers = df_filtered["Farmer Name"].nunique()
    avg_irrigations = round(df_filtered["No of Irrigation"].mean(), 2)
    avg_yield = round(df_filtered["Yield"].mean(), 2)

    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    kpi1.metric("Total Devices", total_devices)
    kpi2.metric("Total Farmers", total_farmers)
    kpi3.metric("Avg No. of Irrigations", avg_irrigations)
    kpi4.metric("Avg Yield (tons/acre)", avg_yield)
    kpi5.metric("Season", "Kharif 2024")

    # --- No. of Irrigation Chart ---
    st.subheader("No. of Irrigations (Village-wise)")
    fig1, ax1 = plt.subplots(figsize=(8, 4))
    df_filtered.groupby("Village Name")["No of Irrigation"].mean().plot(kind="bar", ax=ax1)
    ax1.set_ylabel("Avg Irrigations")
    ax1.set_xlabel("Village")
    ax1.bar_label(ax1.containers[0])
    st.pyplot(fig1)

    # --- Distribution Curve (Irrigation & Water) ---
    st.subheader("Distribution of Irrigation & Total Water")
    fig2, ax2 = plt.subplots(figsize=(8, 4))
    df_filtered["No of Irrigation"].plot(kind="kde", ax=ax2, label="No of Irrigation")
    df_filtered["Total Water"].plot(kind="kde", ax=ax2, label="Total Water (inches)")
    ax2.set_xlabel("Value")
    ax2.set_ylabel("Density")
    ax2.legend()
    st.pyplot(fig2)

    # --- Yield Chart ---
    st.subheader("Yield (Village-wise)")
    fig3, ax3 = plt.subplots(figsize=(8, 4))
    df_filtered.groupby("Village Name")["Yield"].mean().plot(kind="bar", ax=ax3, color="orange")
    ax3.set_ylabel("Avg Yield (tons/acre)")
    ax3.set_xlabel("Village")
    ax3.bar_label(ax3.containers[0])
    st.pyplot(fig3)

    # --- Village-wise Avg Table ---
    st.subheader("Village-wise Averages")
    village_table = df_filtered.groupby("Village Name").agg({
        "No of Irrigation": "mean",
        "Total Water": "mean",
        "Yield": "mean"
    }).reset_index()
    st.dataframe(village_table)

# =========================
# TAB 2: Farmer Summary
# =========================
with tab2:
    st.header("Farmer-wise Irrigation & Details")

    farmers = df_farmer["FarmerName"].dropna().unique().tolist()
    selected_farmer = st.selectbox("Select Farmer", farmers)

    farmer_data = df_farmer[df_farmer["FarmerName"] == selected_farmer]

    # Farmer details table
    st.subheader("Farmer Personal Details")
    detail_cols = ["FarmerName", "FatherName", "MobileNumber", "VillageName", "DeviceID"]
    farmer_details = farmer_data[detail_cols].drop_duplicates()
    st.table(farmer_details)

    # Irrigation Line Chart
    st.subheader("Irrigation Moisture Trend")
    fig4, ax4 = plt.subplots(figsize=(10, 4))
    farmer_data = farmer_data.sort_values("CreateDate")
    ax4.plot(farmer_data["CreateDate"], farmer_data["CalculatedValue"], marker="o")
    ax4.set_xlabel("Date")
    ax4.set_ylabel("Moisture (%)")
    ax4.set_title(f"Irrigation Trend - {selected_farmer}")
    st.pyplot(fig4)
