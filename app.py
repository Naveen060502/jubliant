import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

# Load the Excel file (only the required sheet)
df = pd.read_excel(
    "Jubliant_sugarcane_project-2024_summary.xlsx",
    sheet_name="Summary_excluding_outliers",
    engine="openpyxl"
)

# Set up navigation (2 dashboards)
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Overall Summary", "Farmer Summary"])

# ---------------- Sheet 1: Overall Summary ----------------
if page == "Overall Summary":
    st.title("🚜 Jubiliant Sugarcane Project - Overall Summary")

    # Total devices and farmers
    total_devices = df["Device ID"].nunique() if "Device ID" in df.columns else 0
    total_farmers = df["Farmer Name"].nunique() if "Farmer Name" in df.columns else 0

    col1, col2 = st.columns(2)
    col1.metric("Total Devices", total_devices)
    col2.metric("Total Farmers", total_farmers)

    # Village filter
    if "Village Name" in df.columns:
        villages = ["All"] + df["Village Name"].dropna().unique().tolist()
        selected_village = st.selectbox("Select Village", villages)

        village_df = df.copy()
        if selected_village != "All":
            village_df = village_df[village_df["Village Name"] == selected_village]

        # Column chart - Yield
        if "Yield (quintal/acre)" in village_df.columns:
            st.subheader("🌾 Village-wise Yield (quintal/acre)")
            village_yield = village_df.groupby("Village Name")["Yield (quintal/acre)"].mean().reset_index()
            st.bar_chart(village_yield.set_index("Village Name"))

        # KDE plots (bell-shaped curves)
        st.subheader("📈 Distribution of Irrigation & Water Usage (KDE Curves)")
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.kdeplot(village_df["No of Irrigation"], label="No of Irrigation", fill=True, ax=ax)
        sns.kdeplot(village_df["Total Water (lakh L/acre)"], label="Total Water", fill=True, ax=ax)
        sns.kdeplot(village_df["Irrigated Water (lakh L/acre)"], label="Irrigated Water", fill=True, ax=ax)
        sns.kdeplot(village_df["Rain Water (lakh L/acre)"], label="Rain Water", fill=True, ax=ax)
        ax.set_xlabel("Values")
        ax.set_ylabel("Density")
        ax.legend()
        st.pyplot(fig)

        # Table moved to end
        village_summary = village_df.groupby("Village Name").agg({
            "No of Irrigation": "mean",
            "Total Water (lakh L/acre)": "mean",
            "Irrigated Water (lakh L/acre)": "mean",
            "Rain Water (lakh L/acre)": "mean",
            "Yield (quintal/acre)": "mean"
        }).reset_index()

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

        st.bar_chart(farmer_summary.set_index("Farmer Name")[[
            "No of Irrigation",
            "Total Water (lakh L/acre)",
            "Irrigated Water (lakh L/acre)",
            "Rain Water (lakh L/acre)"
        ]])

        st.subheader("📋 Farmer Summary Table")
        st.dataframe(farmer_summary)
    else:
        st.warning("No data available for selected filters")
