import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy.stats import norm

# Load the Excel file (Summary_excluding_outliers sheet only)
file_path = "Jubliant_sugarcane_project-2024_summary.xlsx"
df = pd.read_excel(file_path, sheet_name="Summary_excluding_outliers")

st.set_page_config(page_title="Sugarcane Project Dashboard", layout="wide")

# ===================== Dashboard Title =====================
st.title("🌾 Sugarcane Project Dashboard - Kharif 2024")

# ===================== Top Summary Metrics =====================
col1, col2, col3, col4, col5 = st.columns(5)

total_devices = df["Device ID"].nunique() if "Device ID" in df.columns else 0
total_farmers = df["Farmer Name"].nunique() if "Farmer Name" in df.columns else 0
avg_irrigation = df["No of Irrigation"].mean() if "No of Irrigation" in df.columns else 0
avg_yield = df["Yield (quintal/acre)"].mean() if "Yield (quintal/acre)" in df.columns else 0
season_name = "Kharif 2024"

col1.metric("📟 Total Devices", total_devices)
col2.metric("👨‍🌾 Total Farmers", total_farmers)
col3.metric("💧 Avg No. of Irrigation", f"{avg_irrigation:.2f}")
col4.metric("🌱 Avg Yield (quintal/acre)", f"{avg_yield:.2f}")
col5.metric("🗓️ Season", season_name)

st.markdown("---")

# ===================== No. of Irrigation Chart =====================
if "Farmer Name" in df.columns and "No of Irrigation" in df.columns:
    st.subheader("📊 No. of Irrigation (Farmer Wise)")
    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.bar(df["Farmer Name"], df["No of Irrigation"], color="skyblue")

    # Add data labels
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f"{height:.0f}", 
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha="center", va="bottom", fontsize=8)
    
    ax.set_xlabel("Farmer")
    ax.set_ylabel("No. of Irrigation")
    ax.set_title("Farmer-wise Irrigation Count")
    plt.xticks(rotation=90)
    st.pyplot(fig)

st.markdown("---")

# ===================== Bell Shape Distribution =====================
st.subheader("🔔 Distribution of Irrigation & Total Water")

fig, ax = plt.subplots(figsize=(10, 6))

# Irrigation data
if "Irrigated Water (lakh L/acre)" in df.columns:
    irrigation_data = df["Irrigated Water (lakh L/acre)"].dropna()
    sns.kdeplot(irrigation_data, fill=True, color="blue", label="No of Irrigation", ax=ax)

    # Overlay Gaussian Fit
    mu, sigma = irrigation_data.mean(), irrigation_data.std()
    x = np.linspace(irrigation_data.min(), irrigation_data.max(), 100)
    ax.plot(x, norm.pdf(x, mu, sigma), "b--")

# Total Water data
if "Total Water (lakh L/acre)" in df.columns:
    water_data = df["Total Water (lakh L/acre)"].dropna()
    sns.kdeplot(water_data, fill=True, color="green", label="Total Water", ax=ax)

    mu_w, sigma_w = water_data.mean(), water_data.std()
    x_w = np.linspace(water_data.min(), water_data.max(), 100)
    ax.plot(x_w, norm.pdf(x_w, mu_w, sigma_w), "g--")

ax.set_title("Bell Curve Distribution of Irrigation & Total Water")
ax.set_xlabel("Value")
ax.set_ylabel("Density")
ax.legend()
st.pyplot(fig)

st.markdown("---")

# ===================== Yield Chart =====================
if "Farmer Name" in df.columns and "Yield (quintal/acre)" in df.columns:
    st.subheader("📊 Yield (Farmer Wise)")
    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.bar(df["Farmer Name"], df["Yield (quintal/acre)"], color="orange")

    # Add data labels
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f"{height:.1f}", 
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha="center", va="bottom", fontsize=8)
    
    ax.set_xlabel("Farmer")
    ax.set_ylabel("Yield (quintal/acre)")
    ax.set_title("Farmer-wise Yield")
    plt.xticks(rotation=90)
    st.pyplot(fig)

st.markdown("---")

# ===================== Village-wise Summary Table =====================
st.subheader("🏘️ Village-wise Average Summary")

if "Village" in df.columns:
    village_summary = df.groupby("Village").agg({
        "No of Irrigation": "mean",
        "Total Water (lakh L/acre)": "mean",
        "Irrigated Water (lakh L/acre)": "mean" if "Irrigated Water (lakh L/acre)" in df.columns else "mean",
        "Rain Water (lakh L/acre)": "mean" if "Rain Water (lakh L/acre)" in df.columns else "mean",
        "Yield (quintal/acre)": "mean"
    }).reset_index()

    st.dataframe(village_summary.round(2))
