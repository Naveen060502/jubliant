import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# Load Excel (Summary sheet only)
df = pd.read_excel(
    "Jubliant_sugarcane_project-2024_summary.xlsx",
    sheet_name="Summary_excluding_outliers",
    engine="openpyxl"
)

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Overall Summary", "Farmer Summary"])

# ---------------- Sheet 1: Overall Summary ----------------
if page == "Overall Summary":
    st.title("🚜 Jubiliant Sugarcane Project - Overall Summary")

    # Total devices and farmers
    total_devices = df["Device ID"].nunique() if "Device ID" in df.columns else 0
    total_farmers = df["Farmer Name"].nunique() if "Farmer Name" in df.columns else 0
    avg_irrigation = df["No of Irrigation"].mean() if "No of Irrigation" in df.columns else 0
    avg_yield = df["Yield (quintal/acre)"].mean() if "Yield (quintal/acre)" in df.columns else 0

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Devices", total_devices)
    col2.metric("Total Farmers", total_farmers)
    col3.metric("Avg Irrigation", f"{avg_irrigation:.2f}")
    col4.metric("Avg Yield", f"{avg_yield:.2f}")
    col5.metric("Season", "Kharif 2024")

    # Village-wise summary
    if "Village Name" in df.columns:
        village_summary = df.groupby("Village Name").agg({
            "No of Irrigation": "mean",
            "Total Water (lakh L/acre)": "mean",
            "Irrigated Water (lakh L/acre)": "mean",
            "Rain Water (lakh L/acre)": "mean",
            "Yield (quintal/acre)": "mean"
        }).reset_index()

        # 1️⃣ Column Chart - Irrigation
        st.subheader("📊 Village-wise Average No. of Irrigation")
        st.bar_chart(village_summary.set_index("Village Name")["No of Irrigation"])

        # 2️⃣ Bell Shape Curves - Irrigation & Total Water
        st.subheader("🔔 Distribution of Irrigation & Total Water")

        fig, ax = plt.subplots(figsize=(8, 5))
        x_irrig = np.linspace(df["Irrigated Water (lakh L/acre)"].min(), df["Irrigated Water (lakh L/acre)"].max(), 200)
        mu_irrig, sigma_irrig = df["Irrigated Water (lakh L/acre)"].mean(), df["Irrigated Water (lakh L/acre)"].std()
        y_irrig = (1 / (sigma_irrig * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x_irrig - mu_irrig) / sigma_irrig) ** 2)
        ax.plot(x_irrig, y_irrig, label="Irrigated Water (lakh L/acre)", color="blue")

        x_water = np.linspace(df["Total Water (lakh L/acre)"].min(), df["Total Water (lakh L/acre)"].max(), 200)
        mu_water, sigma_water = df["Total Water (lakh L/acre)"].mean(), df["Total Water (lakh L/acre)"].std()
        y_water = (1 / (sigma_water * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x_water - mu_water) / sigma_water) ** 2)
        ax.plot(x_water, y_water, label="Total Water", color="green")

        ax.set_title("Bell Curve Distribution")
        ax.legend()
        st.pyplot(fig)

        # 3️⃣ Column Chart - Yield
        st.subheader("🌾 Village-wise Average Yield (quintal/acre)")
        st.bar_chart(village_summary.set_index("Village Name")["Yield (quintal/acre)"])

        # 4️⃣ End of page - Village-wise Table
        st.subheader("📍 Village-wise Average Summary")
        st.dataframe(village_summary)

# ---------------- Sheet 2: Farmer Summary ----------------
elif page == "Farmer Summary":
    st.title("👨‍🌾 Farmer-wise Summary")

    # Filters
    villages = ["All"] + df["Village Name"].dropna().unique().tolist()
    farmers = ["All"] + df["Farmer Name"].dropna().unique().tolist()

    selected_village = st.sidebar.selectbox("Select Village", villages)
    selected_farmer = st.sidebar.selectbox("Select Farmer", farmers)

    farmer_df = df.copy()
    if selected_village != "All":
        farmer_df = farmer_df[farmer_df["Village Name"] == selected_village]
    if selected_farmer != "All":
        farmer_df = farmer_df[farmer_df["Farmer Name"] == selected_farmer]

    # Farmer summary
    if not farmer_df.empty:
        farmer_summary = farmer_df.groupby("Farmer Name").agg({
            "No of Irrigation": "sum",
            "Total Water (lakh L/acre)": "sum",
            "Irrigated Water (lakh L/acre)": "sum",
            "Rain Water (lakh L/acre)": "sum",
            "Yield (quintal/acre)": "mean"
        }).reset_index()

        st.dataframe(farmer_summary)

        st.bar_chart(farmer_summary.set_index("Farmer Name")[[
            "No of Irrigation",
            "Total Water (lakh L/acre)",
            "Irrigated Water (lakh L/acre)",
            "Rain Water (lakh L/acre)"
        ]])
    else:
        st.warning("No data available for selected filters")
