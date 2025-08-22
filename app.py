import pandas as pd
import streamlit as st

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

    # Village-wise averages
    if "Village Name" in df.columns:
        village_summary = df.groupby("Village Name").agg({
            "No of Irrigation": "mean",
            "Total Water (lakh L/acre)": "mean",
            "Irrigated Water (lakh L/acre)": "mean",
            "Rain Water (lakh L/acre)": "mean"
        }).reset_index()

        st.subheader("📍 Village-wise Average Summary")
        st.dataframe(village_summary)

        st.bar_chart(village_summary.set_index("Village Name")[["No of Irrigation","Total Water (lakh L/acre)","Irrigated Water (lakh L/acre)","Rain Water (lakh L/acre)"]])

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
            "Rain Water (lakh L/acre)": "sum"
        }).reset_index()

        st.dataframe(farmer_summary)

        st.bar_chart(farmer_summary.set_index("Farmer Name")[["No of Irrigation","Total Water (lakh L/acre)","Irrigated Water (lakh L/acre)","Rain Water (lakh L/acre)"]])
    else:
        st.warning("No data available for selected filters")



