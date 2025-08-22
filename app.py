import pandas as pd
import streamlit as st
import plotly.express as px

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

    # Total devices and farmers
    total_devices = df["Device ID"].nunique() if "Device ID" in df.columns else 0
    total_farmers = df["Farmer Name"].nunique() if "Farmer Name" in df.columns else 0

    col1, col2 = st.columns(2)
    col1.metric("Total Devices", total_devices)
    col2.metric("Total Farmers", total_farmers)

    # Village filter
    villages = ["All"] + df["Village Name"].dropna().unique().tolist()
    selected_village = st.sidebar.selectbox("Select Village", villages)

    filtered_df = df.copy()
    if selected_village != "All":
        filtered_df = filtered_df[filtered_df["Village Name"] == selected_village]

    # 📍 Village-wise averages
    if "Village Name" in filtered_df.columns:
        village_summary = filtered_df.groupby("Village Name").agg({
            "No of Irrigation": "mean",
            "Total Water (lakh L/acre)": "mean",
            "Irrigated Water (lakh L/acre)": "mean",
            "Rain Water (lakh L/acre)": "mean",
            "Yield (quintal/acre)": "mean"
        }).reset_index()

        st.subheader("📍 Village-wise Average Summary")
        st.dataframe(village_summary)

        # --- Chart 1: Column chart for No of Irrigation ---
        st.subheader("📊 No of Irrigations per Village")
        fig_bar = px.bar(
            village_summary,
            x="Village Name",
            y="No of Irrigation",
            title="Village-wise No of Irrigations",
            text_auto=True,
            color="Village Name"
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        # --- Chart 2: Column chart for Yield ---
        st.subheader("🌾 Yield (quintal/acre) per Village")
        fig_yield = px.bar(
            village_summary,
            x="Village Name",
            y="Yield (quintal/acre)",
            title="Village-wise Yield",
            text_auto=True,
            color="Village Name"
        )
        st.plotly_chart(fig_yield, use_container_width=True)

        # --- Chart 3: Normalized Bell Curves for Water Usage ---
        st.subheader("🔔 Distribution of Water Usage (Normalized)")
        melted = filtered_df.melt(
            id_vars=["Village Name"],
            value_vars=[
                "No of Irrigation",
                "Total Water (lakh L/acre)",
                "Irrigated Water (lakh L/acre)",
                "Rain Water (lakh L/acre)"
            ],
            var_name="Metric",
            value_name="Value"
        )

        fig_dist = px.histogram(
            melted,
            x="Value",
            color="Metric",
            marginal="box",  # adds boxplot above
            histnorm="probability density",  # normalized bell-shape
            barmode="overlay",
            opacity=0.6
        )
        fig_dist.update_traces(marker_line_width=1, marker_line_color="white")
        st.plotly_chart(fig_dist, use_container_width=True)

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
            "Yield (quintal/acre)": "mean"   # yield usually avg, not sum
        }).reset_index()

        st.subheader("👨‍🌾 Farmer Summary Table")
        st.dataframe(farmer_summary)

        # Chart for Farmer comparison
        st.subheader("📊 Farmer-wise Irrigation, Water & Yield")
        fig_farmer = px.bar(
            farmer_summary,
            x="Farmer Name",
            y=["No of Irrigation",
               "Total Water (lakh L/acre)",
               "Irrigated Water (lakh L/acre)",
               "Rain Water (lakh L/acre)",
               "Yield (quintal/acre)"],
            barmode="group",
            title="Farmer-wise Summary"
        )
        st.plotly_chart(fig_farmer, use_container_width=True)
    else:
        st.warning("No data available for selected filters")
