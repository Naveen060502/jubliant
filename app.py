import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# Load the Excel file (only the required sheet)
df = pd.read_excel(
    "Jubliant_sugarcane_project-2024_summary.xlsx",
    sheet_name="Summary_excluding_outliers",
    engine="openpyxl"
)

# Sidebar Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Overall Summary", "Farmer Summary"])

# ---------------- Sheet 1: Overall Summary ----------------
if page == "Overall Summary":
    st.title("🚜 Jubiliant Sugarcane Project - Overall Summary")

    # --- Village Filter ---
    villages = ["All"] + df["Village Name"].dropna().unique().tolist()
    selected_village = st.sidebar.selectbox("Select Village", villages)

    # Prepare village summary
    village_summary = df.groupby("Village Name").agg({
        "No of Irrigation": "mean",
        "Total Water (lakh L/acre)": "mean",
        "Irrigated Water (lakh L/acre)": "mean",
        "Rain Water (lakh L/acre)": "mean",
        "Yield (quintal/acre)": "mean"
    }).reset_index()

    if selected_village != "All":
        village_summary = village_summary[village_summary["Village Name"] == selected_village]

    # --- Top Metrics ---
    total_devices = df["Device ID"].nunique() if "Device ID" in df.columns else 0
    total_farmers = df["Farmer Name"].nunique() if "Farmer Name" in df.columns else 0
    avg_irrigation = village_summary["No of Irrigation"].mean()
    avg_yield = village_summary["Yield (quintal/acre)"].mean()

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Devices", total_devices)
    col2.metric("Total Farmers", total_farmers)
    col3.metric("Avg No. of Irrigations", f"{avg_irrigation:.2f}")
    col4.metric("Avg Yield (qtl/acre)", f"{avg_yield:.2f}")
    col5.metric("Season", "Kharif 2024")

    # --- No of Irrigation Column Chart ---
    st.subheader("📊 Village-wise No of Irrigations")
    fig, ax = plt.subplots(figsize=(8,5))
    bars = ax.bar(village_summary["Village Name"], village_summary["No of Irrigation"], color="skyblue")
    ax.set_ylabel("No of Irrigations")
    ax.set_xlabel("Village")
    ax.set_title("Average No of Irrigations by Village")
    ax.tick_params(axis="x", rotation=45)

    # Add data labels
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, yval, f"{yval:.1f}", ha="center", va="bottom")

    st.pyplot(fig)

    # --- Bell Shape Curves (No of Irrigation & Total Water) ---
    st.subheader("📈 Distribution of Irrigation & Total Water (Bell Curves)")
    fig, ax = plt.subplots(figsize=(8,5))

    for col, color in zip(["Irrigated Water (lakh L/acre)", "Total Water (lakh L/acre)"], ["blue", "green"]):
        data = df[col].dropna()
        mu, sigma = np.mean(data), np.std(data)
        x = np.linspace(mu - 3*sigma, mu + 3*sigma, 100)
        y = 1/(sigma * np.sqrt(2*np.pi)) * np.exp(-0.5*((x-mu)/sigma)**2)
        ax.plot(x, y, label=f"{col} (μ={mu:.1f}, σ={sigma:.1f})", color=color)

    ax.set_title("Normal Distribution of Irrigation & Total Water")
    ax.legend()
    st.pyplot(fig)

    # --- Yield Column Chart ---
    st.subheader("🌾 Village-wise Yield (quintal/acre)")
    fig, ax = plt.subplots(figsize=(8,5))
    bars = ax.bar(village_summary["Village Name"], village_summary["Yield (quintal/acre)"], color="orange")
    ax.set_ylabel("Yield (qtl/acre)")
    ax.set_xlabel("Village")
    ax.set_title("Average Yield by Village")
    ax.tick_params(axis="x", rotation=45)

    # Add data labels
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, yval, f"{yval:.1f}", ha="center", va="bottom")

    st.pyplot(fig)

    # --- Village-wise Table (End of Page) ---
    st.subheader("📍 Village-wise Average Summary")
    st.dataframe(village_summary)

# ---------------- Sheet 2: Farmer Summary ----------------
elif page == "Farmer Summary":
    st.title("👨‍🌾 Farmer-wise Summary")

    villages = ["All"] + df["Village Name"].dropna().unique().tolist()
    farmers = ["All"] + df["Farmer Name"].dropna().unique().tolist()

    selected_village = st.sidebar.selectbox("Select Village", villages)
    selected_farmer = st.sidebar.selectbox("Select Farmer", farmers)

    farmer_df = df.copy()
    if selected_village != "All":
        farmer_df = farmer_df[farmer_df["Village Name"] == selected_village]
    if selected_farmer != "All":
        farmer_df = farmer_df[farmer_df["Farmer Name"] == selected_farmer]

    if not farmer_df.empty:
        farmer_summary = farmer_df.groupby("Farmer Name").agg({
            "No of Irrigation": "sum",
            "Total Water (lakh L/acre)": "sum",
            "Irrigated Water (lakh L/acre)": "sum",
            "Rain Water (lakh L/acre)": "sum",
            "Yield (quintal/acre)": "mean"
        }).reset_index()

        st.dataframe(farmer_summary)
    else:
        st.warning("No data available for selected filters")
