import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

# Load Excel sheet
df = pd.read_excel(
    "Jubliant_sugarcane_project-2024_summary.xlsx",
    sheet_name="Summary_excluding_outliers",
    engine="openpyxl"
)

# Sidebar filters
# Sidebar filters (default = nothing selected)
villages = df["Village Name"].dropna().unique().tolist()
selected_villages = st.sidebar.multiselect(
    "Select Village(s)", 
    options=villages, 
    default=[]  # <-- nothing selected by default
)

# If no selection, show all villages
if selected_villages:
    df_filtered = df[df["Village Name"].isin(selected_villages)]
else:
    df_filtered = df.copy()


# Prepare village summary
village_summary = df.groupby("Village Name").agg({
    "No of Irrigation": "mean",
    "Yield (quintal/acre)": "mean",
    "Total Water (lakh L/acre)": "mean",
    "Irrigated Water (lakh L/acre)": "mean",
    "Rain Water (lakh L/acre)": "mean"
}).reset_index()

# ---------------- Dashboard ----------------
st.title("Jubiliant Sugarcane Project")

# KPIs
total_devices = df["Device ID"].nunique() if "Device ID" in df.columns else 0
total_farmers = df["Farmer Name"].nunique() if "Farmer Name" in df.columns else 0
avg_irrigation = df["No of Irrigation"].mean().round(2)
avg_yield = df["Yield (quintal/acre)"].mean().round(2)

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Devices", total_devices)
col2.metric("Total Farmers", total_farmers)
col3.metric("Avg No of Irrigation", avg_irrigation)
col4.metric("Avg Yield (qtl/acre)", avg_yield)
col5.metric("Season","Kharif 24")

# ---------------- Chart 1: No of Irrigation ----------------
st.subheader("📊 Village-wise No of Irrigation")
fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.bar(village_summary["Village Name"], village_summary["No of Irrigation"], color="skyblue")
ax.set_ylabel("No of Irrigation")
ax.set_xlabel("Village")
ax.set_title("Village-wise No of Irrigation")
ax.bar_label(bars, fmt="%.1f", padding=3)
st.pyplot(fig)

# ---------------- Chart 2: Distribution Curves ----------------
st.subheader("🔔 Distribution of Irrigation & Total Water")
fig, ax = plt.subplots(figsize=(8, 5))
sns.kdeplot(df["Irrigated Water (lakh L/acre)"], label="Irrigation Water", fill=True, ax=ax)
sns.kdeplot(df["Total Water (lakh L/acre)"], label="Total Water", fill=True, ax=ax)
ax.set_title("Distribution (Bell-Shaped Curves)")
ax.set_xlabel("Value")
ax.set_ylabel("Density")
ax.legend()
st.pyplot(fig)

# ---------------- Chart 3: Yield ----------------
st.subheader("🌾 Village-wise Yield (quintal/acre)")
fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.bar(village_summary["Village Name"], village_summary["Yield (quintal/acre)"], color="green")
ax.set_ylabel("Yield (qtl/acre)")
ax.set_xlabel("Village")
ax.set_title("Village-wise Yield")
ax.bar_label(bars, fmt="%.1f", padding=3)
st.pyplot(fig)

# ---------------- Table ----------------
st.subheader("📍 Village-wise Average Summary")
st.dataframe(village_summary)




