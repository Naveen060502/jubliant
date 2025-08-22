import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Load Excel
file_path = "moist_data.xlsx"
df_summary = pd.read_excel(file_path, sheet_name="Summary_excluding_outliers")
df_farmer = pd.read_excel(file_path, sheet_name="Farmer summary")

# Ensure correct dtypes
if "CreateDate" in df_farmer.columns:
    df_farmer["CreateDate"] = pd.to_datetime(df_farmer["CreateDate"], errors="coerce")

# Streamlit Page Setup
st.set_page_config(page_title="Jubiliant Sugarcane Project Dashboard", layout="wide")

st.title("🌾 Jubiliant Sugarcane Project Dashboard")

# Tabs
tab1, tab2 = st.tabs(["📊 Village Summary", "👨‍🌾 Farmer Summary"])

# -------------------------
# TAB 1: Village Summary
# -------------------------
with tab1:
    st.subheader("📊 Village Level Summary")

    # Village filter
    all_villages = df_summary["Village Name"].dropna().unique().tolist()
    selected_villages = st.multiselect(
        "Select Village(s)", options=all_villages, default=[]
    )

    # Apply filter
    if selected_villages:
        df_village = df_summary[df_summary["Village Name"].isin(selected_villages)]
    else:
        df_village = df_summary.copy()

    # KPIs
    total_devices = df_village["Total Devices"].sum()
    total_farmers = df_village["Total Farmers"].sum()
    avg_irrigation = df_village["No of Irrigation"].mean().round(2)
    avg_yield = df_village["Yield (quintal/acre)"].mean().round(2)

    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    kpi1.metric("📟 Total Devices", total_devices)
    kpi2.metric("👨‍🌾 Total Farmers", total_farmers)
    kpi3.metric("💧 Avg No. of Irrigation", avg_irrigation)
    kpi4.metric("🌾 Avg Yield (qtl/acre)", avg_yield)
    kpi5.metric("🗓️ Season", "Kharif 2024")

    # No. of Irrigation Column Chart
    fig_irrig = px.bar(
        df_village,
        x="Village Name",
        y="No of Irrigation",
        text="No of Irrigation",
        title="🌊 Average No. of Irrigations (Village-wise)",
    )
    fig_irrig.update_traces(textposition="outside")
    st.plotly_chart(fig_irrig, use_container_width=True)

    # Distribution (Bell Curve)
    irrigation_data = df_village["No of Irrigation"].dropna()
    totalwater_data = df_village["Total Water"].dropna()

    if not irrigation_data.empty:
        x_irrig = np.linspace(irrigation_data.min(), irrigation_data.max(), 100)
        y_irrig = (
            1 / (irrigation_data.std() * np.sqrt(2 * np.pi))
        ) * np.exp(-0.5 * ((x_irrig - irrigation_data.mean()) / irrigation_data.std()) ** 2)

        fig_curve = go.Figure()
        fig_curve.add_trace(go.Scatter(x=x_irrig, y=y_irrig, mode="lines", name="Irrigation"))

        if not totalwater_data.empty:
            x_tw = np.linspace(totalwater_data.min(), totalwater_data.max(), 100)
            y_tw = (
                1 / (totalwater_data.std() * np.sqrt(2 * np.pi))
            ) * np.exp(-0.5 * ((x_tw - totalwater_data.mean()) / totalwater_data.std()) ** 2)
            fig_curve.add_trace(go.Scatter(x=x_tw, y=y_tw, mode="lines", name="Total Water"))

        fig_curve.update_layout(title="📈 Distribution of Irrigation & Total Water (Bell Curve)")
        st.plotly_chart(fig_curve, use_container_width=True)

    # Yield Column Chart
    fig_yield = px.bar(
        df_village,
        x="Village Name",
        y="Yield (quintal/acre)",
        text="Yield (quintal/acre)",
        title="🌾 Yield (qtl/acre) Village-wise",
    )
    fig_yield.update_traces(textposition="outside")
    st.plotly_chart(fig_yield, use_container_width=True)

    # Village Summary Table
    st.subheader("📋 Village-wise Average Summary")
    st.dataframe(df_village)

# -------------------------
# TAB 2: Farmer Summary
# -------------------------
with tab2:
    st.subheader("👨‍🌾 Farmer Level Summary")

    # Farmer filter
    all_farmers = df_farmer["FarmerName"].dropna().unique().tolist()
    selected_farmers = st.multiselect(
        "Select Farmer(s)", options=all_farmers, default=[]
    )

    if selected_farmers:
        df_filt = df_farmer[df_farmer["FarmerName"].isin(selected_farmers)]
    else:
        df_filt = df_farmer.copy()

    for farmer in df_filt["FarmerName"].unique():
        st.markdown(f"### 👨‍🌾 Farmer: {farmer}")
        f_df = df_filt[df_filt["FarmerName"] == farmer]

        # Personal details
        details = f_df[
            ["FarmerName", "FatherName", "MobileNumber", "VillageName", "DeviceID"]
        ].drop_duplicates()

        st.table(details)

        # Irrigation Line Chart
        if not f_df.empty:
            fig_line = px.line(
                f_df,
                x="CreateDate",
                y="CalculatedValue",
                title=f"💧 Irrigation Trend for {farmer}",
                markers=True,
            )
            st.plotly_chart(fig_line, use_container_width=True)
