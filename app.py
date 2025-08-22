import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# -----------------------------
# Load Data
# -----------------------------
@st.cache_data
def load_summary():
    return pd.read_excel("Jubliant_sugarcane_project-2024_summary.xlsx", sheet_name="Summary_excluding_outliers")

@st.cache_data
def load_farmer():
    return pd.read_excel("moist_data.xlsx")

summary_df = load_summary()
farmer_df = load_farmer()

# -----------------------------
# Streamlit App
# -----------------------------
st.set_page_config(page_title="Jubilant Sugarcane Project Dashboard", layout="wide")

st.title("🌾 Jubilant Sugarcane Project Dashboard")

# Tabs
tab1, tab2 = st.tabs(["📊 Overall Summary", "👩‍🌾 Farmer Summary"])

# -----------------------------
# Tab 1 - Overall Summary
# -----------------------------
with tab1:
    st.subheader("📊 Overall Summary - Kharif 2024")

    # Village filter
    villages = summary_df["VillageName"].unique().tolist()
    selected_villages = st.multiselect(
        "Select Village(s)", villages, default=villages, placeholder="Select villages"
    )

    if selected_villages:
        filtered_summary = summary_df[summary_df["Village Name"].isin(selected_villages)]
    else:
        filtered_summary = summary_df.copy()

    # KPIs
    total_devices = filtered_summary["Device ID"].nunique()
    total_farmers = filtered_summary["Farmer Name"].nunique()
    avg_irrigation = filtered_summary["No of Irrigation"].mean()
    avg_yield = filtered_summary["Yield (quintal/acre)"].mean()

    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    kpi1.metric("Total Devices", total_devices)
    kpi2.metric("Total Farmers", total_farmers)
    kpi3.metric("Avg No. of Irrigation", f"{avg_irrigation:.2f}")
    kpi4.metric("Avg Yield (qtl/acre)", f"{avg_yield:.2f}")
    kpi5.metric("Season", "Kharif 2024")

    # Charts
    st.markdown("### 🌍 Village-wise Charts")

    col1, col2 = st.columns(2)

    with col1:
        fig, ax = plt.subplots()
        sns.barplot(data=filtered_summary, x="Village Name", y="No of Irrigation", estimator=np.mean, ci=None, ax=ax)
        ax.set_title("Village-wise Avg No of Irrigation")
        ax.bar_label(ax.containers[0])
        st.pyplot(fig)

    with col2:
        fig, ax = plt.subplots()
        sns.barplot(data=filtered_summary, x="Village Name", y="Yield (quintal/acre)", estimator=np.mean, ci=None, ax=ax)
        ax.set_title("Village-wise Avg Yield")
        ax.bar_label(ax.containers[0])
        st.pyplot(fig)

    # Bell shape curves
    st.markdown("### 🔔 Distribution Curves")
    fig, ax = plt.subplots()
    sns.kdeplot(filtered_summary["Irrigated Water (lakh L/acre)"], fill=True, label="No of Irrigation", ax=ax)
    sns.kdeplot(filtered_summary["Total Water (lakh L/acre)"], fill=True, label="Total Water Used", ax=ax)
    ax.set_title("Distribution of Irrigation & Total Water")
    ax.legend()
    st.pyplot(fig)

    # Village-wise avg table
    st.markdown("### 📋 Village-wise Averages")
    village_table = filtered_summary.groupby("VillageName").agg({
        "No of Irrigation": "mean",
        "Total Water (lakh L/acre)": "mean",
        "Irrigated Water (lakh L/acre)": "mean",
        "Rain Water (lakh L/acre)": "mean",
        "Yield (quintal/acre)": "mean"
    }).reset_index()
    st.dataframe(village_table.style.format("{:.2f}"))

# -----------------------------
# Tab 2 - Farmer Summary
# -----------------------------
with tab2:
    st.subheader("👩‍🌾 Farmer Summary")

    # Farmer filter
    farmers = farmer_df["Farmer Name"].unique().tolist()
    selected_farmers = st.multiselect(
        "Select Farmer(s)", farmers, default=farmers, placeholder="Select farmers"
    )

    if selected_farmers:
        filtered_farmer = farmer_df[farmer_df["Farmer Name"].isin(selected_farmers)]
    else:
        filtered_farmer = farmer_df.copy()

    # Farmer table
    st.markdown("### 📋 Farmer Details")
    farmer_details = filtered_farmer[["Farmer Name", "Father Name", "Mobile Number", "Village Name", "Device ID"]].drop_duplicates()
    st.dataframe(farmer_details)

    # Irrigation count per farmer
    st.markdown("### 📊 Irrigation Count per Farmer")
    fig, ax = plt.subplots()
    irrigation_counts = filtered_farmer.groupby("Farmer Name")["No of Irrigation"].mean().reset_index()
    sns.barplot(data=irrigation_counts, x="Farmer Name", y="No of Irrigation", ax=ax)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")
    ax.bar_label(ax.containers[0])
    st.pyplot(fig)

    # Moisture line chart
    st.markdown("### 📈 Moisture Variation Over Time")
    fig, ax = plt.subplots()
    for farmer in filtered_farmer["Farmer Name"].unique():
        subset = filtered_farmer[filtered_farmer["Farmer Name"] == farmer]
        ax.plot(subset["CreateDate"], subset["CalculatedValue"], marker="o", label=farmer)
    ax.set_xlabel("Date")
    ax.set_ylabel("Moisture (%)")
    ax.set_title("Moisture % over Time")
    ax.legend()
    st.pyplot(fig)

