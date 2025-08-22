import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Jubilant Sugarcane Project", layout="wide")

# -----------------------------
# Data loaders (cached)
# -----------------------------
@st.cache_data
def load_summary():
    return pd.read_excel(
        "Jubliant_sugarcane_project-2024_summary.xlsx",
        sheet_name="Summary_excluding_outliers",
        engine="openpyxl"
    )

@st.cache_data
def load_moist():
    df = pd.read_excel("moist_data.xlsx", engine="openpyxl")
    # Ensure datetime for plotting
    if "CreateDate" in df.columns:
        df["CreateDate"] = pd.to_datetime(df["CreateDate"], errors="coerce")
    return df

summary_df = load_summary()
moist_df = load_moist()

# -----------------------------
# Tabs
# -----------------------------
tab1, tab2 = st.tabs(["📊 Overall Summary", "👩‍🌾 Farmer Summary"])

# =========================================================
# TAB 1: OVERALL SUMMARY (Village-wise averages + filter)
# =========================================================
with tab1:
    st.title("🌾 Jubilant Sugarcane Project — Overall Summary")

    # --- Village filter (multi-select; default empty means 'show all') ---
    all_villages = sorted(summary_df["Village Name"].dropna().unique().tolist())
    selected_villages = st.multiselect(
        "Select Village(s) (leave empty to show all)",
        options=all_villages,
        default=[],
        placeholder="Select village(s)"
    )
    if selected_villages:
        df_f = summary_df[summary_df["Village Name"].isin(selected_villages)].copy()
    else:
        df_f = summary_df.copy()

    # --- Build village-wise averages (used for ALL charts on this tab) ---
    agg_cols = {
        "No of Irrigation": "mean",
        "Total Water (lakh L/acre)": "mean",
        "Irrigated Water (lakh L/acre)": "mean",
        "Rain Water (lakh L/acre)": "mean",
        "Yield (quintal/acre)": "mean",
    }
    vill_avg = (
        df_f.groupby("Village Name", dropna=True)
            .agg(agg_cols)
            .reset_index()
            .sort_values("Village Name")
    )

    # --- KPIs (use filtered data) ---
    total_devices = df_f["Device ID"].nunique() if "Device ID" in df_f.columns else 0
    total_farmers = df_f["Farmer Name"].nunique() if "Farmer Name" in df_f.columns else 0
    avg_irrigation = vill_avg["No of Irrigation"].mean() if not vill_avg.empty else 0
    avg_yield = vill_avg["Yield (quintal/acre)"].mean() if not vill_avg.empty else 0

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Total Devices", int(total_devices))
    k2.metric("Total Farmers", int(total_farmers))
    k3.metric("Avg No. of Irrigation", f"{avg_irrigation:.2f}")
    k4.metric("Avg Yield (qtl/acre)", f"{avg_yield:.2f}")
    k5.metric("Season", "Kharif 2024")

    st.divider()

    # 1) Column chart: Village-wise Avg No. of Irrigation (with labels)
    st.subheader("📊 Village-wise Avg No. of Irrigation")
    if vill_avg.empty:
        st.info("No data to display for the selected filter.")
    else:
        fig1, ax1 = plt.subplots(figsize=(10, 5))
        bars1 = ax1.bar(vill_avg["Village Name"], vill_avg["No of Irrigation"], color="#6AAFE6")
        ax1.set_xlabel("Village")
        ax1.set_ylabel("Avg No. of Irrigation")
        ax1.set_title("Average No. of Irrigation by Village")
        ax1.tick_params(axis="x", rotation=40, ha="right")
        # Data labels
        ax1.bar_label(bars1, fmt="%.1f", padding=3)
        st.pyplot(fig1, use_container_width=True)

    # 2) Bell-shaped curves (KDE): Village-average Irrigation & Total Water
    st.subheader("🔔 Distribution (Bell Curves) of Village Averages: Irrigation & Total Water")
    if vill_avg.shape[0] < 2:
        st.info("Need at least 2 villages to render KDE curves.")
    else:
        fig2, ax2 = plt.subplots(figsize=(10, 5))
        # KDE on village-average series (not raw rows)
        # Handle potential zero variance gracefully
        if vill_avg["Irrigated Water (lakh L/acre)"].std() > 0:
            sns.kdeplot(vill_avg["Irrigated Water (lakh L/acre)"], fill=True, label="Irrigated Water", ax=ax2)
        else:
            ax2.plot(vill_avg["Irrigated Water (lakh L/acre)"], np.zeros_like(vill_avg["Irrigated Water (lakh L/acre)"]), label="Irrigated Water")

        if vill_avg["Total Water (lakh L/acre)"].std() > 0:
            sns.kdeplot(vill_avg["Total Water (lakh L/acre)"], fill=True, label="Avg Total Water (lakh L/acre)", ax=ax2)
        else:
            ax2.plot(vill_avg["Total Water (lakh L/acre)"], np.zeros_like(vill_avg["Total Water (lakh L/acre)"]), label="Avg Total Water (lakh L/acre)")

        ax2.set_xlabel("Value")
        ax2.set_ylabel("Density")
        ax2.set_title("KDE of Village-wise Averages")
        ax2.legend()
        st.pyplot(fig2, use_container_width=True)

    # 3) Column chart: Village-wise Avg Yield (with labels)
    st.subheader("🌾 Village-wise Avg Yield (quintal/acre)")
    if vill_avg.empty:
        st.info("No data to display for the selected filter.")
    else:
        fig3, ax3 = plt.subplots(figsize=(10, 5))
        bars3 = ax3.bar(vill_avg["Village Name"], vill_avg["Yield (quintal/acre)"], color="#F4A259")
        ax3.set_xlabel("Village")
        ax3.set_ylabel("Avg Yield (qtl/acre)")
        ax3.set_title("Average Yield by Village")
        ax3.tick_params(axis="x", rotation=40, ha="right")
        # Data labels
        ax3.bar_label(bars3, fmt="%.1f", padding=3)
        st.pyplot(fig3, use_container_width=True)

    # 4) Village-wise Average Table (bottom)
    st.subheader("📍 Village-wise Average Summary")
    if vill_avg.empty:
        st.info("No data to display for the selected filter.")
    else:
        st.dataframe(vill_avg.round(2), use_container_width=True)

# =========================================================
# TAB 2: FARMER SUMMARY (bar chart + details + per-farmer line)
# =========================================================
with tab2:
    st.title("👩‍🌾 Farmer Summary")

    # --- Build farmer irrigation from SUMMARY sheet (not in moist data) ---
    # We'll use average No of Irrigation per farmer from the summary sheet
    if "Farmer Name" in summary_df.columns and "No of Irrigation" in summary_df.columns:
        farmer_irrig = (
            summary_df.groupby("Farmer Name", dropna=True)["No of Irrigation"]
            .mean()
            .reset_index()
            .rename(columns={"Farmer Name": "FarmerName", "No of Irrigation": "Avg Irrigation"})
            .sort_values("FarmerName")
        )
    else:
        farmer_irrig = pd.DataFrame(columns=["FarmerName", "Avg Irrigation"])

    # --- Farmer multiselect (default empty -> show all) for chart/table ---
    all_farmers = sorted(
        pd.unique(
            pd.concat([
                farmer_irrig["FarmerName"],
                moist_df.get("FarmerName", pd.Series(dtype=object))
            ], ignore_index=True).dropna()
        ).tolist()
    )
    selected_farmers = st.multiselect(
        "Select Farmer(s) (leave empty to show all)",
        options=all_farmers,
        default=[],
        placeholder="Select farmer(s)"
    )

    # Filter both frames by selected farmers (if any)
    if selected_farmers:
        farmer_irrig_f = farmer_irrig[farmer_irrig["FarmerName"].isin(selected_farmers)].copy()
        moist_f = moist_df[moist_df["FarmerName"].isin(selected_farmers)].copy()
    else:
        farmer_irrig_f = farmer_irrig.copy()
        moist_f = moist_df.copy()

    # --- Column chart: Avg Irrigation per Farmer (labels) ---
    st.subheader("📊 Average No. of Irrigation per Farmer")
    if farmer_irrig_f.empty:
        st.info("No farmer irrigation data available.")
    else:
        fig4, ax4 = plt.subplots(figsize=(10, 5))
        bars4 = ax4.bar(farmer_irrig_f["FarmerName"], farmer_irrig_f["Avg Irrigation"], color="#6AAFE6")
        ax4.set_xlabel("Farmer")
        ax4.set_ylabel("Avg No. of Irrigation")
        ax4.set_title("Average No. of Irrigation per Farmer")
        ax4.tick_params(axis="x", rotation=40, ha="right")
        ax4.bar_label(bars4, fmt="%.1f", padding=3)
        st.pyplot(fig4, use_container_width=True)

    st.divider()

    # --- Layout: Details table (left) and per-farmer moisture line chart (right) ---
    left, right = st.columns([1, 2], gap="large")

    with left:
        st.subheader("📋 Farmer Details")
        if moist_f.empty:
            st.info("No moisture dataset rows for the selected farmer(s).")
        else:
            # Deduplicate and keep key columns
            cols = ["FarmerName", "FatherName", "MobileNumber", "Villagename", "DeviceID"]
            present_cols = [c for c in cols if c in moist_f.columns]
            details = moist_f[present_cols].drop_duplicates().sort_values("FarmerName")
            # Rename for nice headings
            rename_map = {"Villagename": "VillageName"}
            details = details.rename(columns=rename_map)
            st.dataframe(details, use_container_width=True)

    with right:
        st.subheader("📈 Moisture (%) over Time — Select a Farmer")
        # Single select to focus one farmer for the line chart
        focus_options = sorted(moist_f["FarmerName"].dropna().unique().tolist()) if not moist_f.empty else []
        focus_farmer = st.selectbox(
            "Choose a farmer for the trend",
            options=focus_options,
            index=0 if len(focus_options) > 0 else None,
            placeholder="Select a farmer"
        )

        if focus_farmer:
            trend = moist_f[moist_f["FarmerName"] == focus_farmer].copy()
            if "CreateDate" in trend.columns and "CalculatedValue" in trend.columns:
                trend = trend.dropna(subset=["CreateDate", "CalculatedValue"]).sort_values("CreateDate")
                if trend.empty:
                    st.info("No dated moisture readings for this farmer.")
                else:
                    fig5, ax5 = plt.subplots(figsize=(10, 5))
                    ax5.plot(trend["CreateDate"], trend["CalculatedValue"], marker="o", linewidth=2)
                    ax5.set_xlabel("CreateDate")
                    ax5.set_ylabel("Moisture (%)")
                    ax5.set_title(f"Moisture % over Time — {focus_farmer}")
                    ax5.grid(True, alpha=0.3)
                    plt.xticks(rotation=30, ha="right")
                    st.pyplot(fig5, use_container_width=True)
            else:
                st.info("Required columns 'CreateDate' and 'CalculatedValue' not found for line chart.")
        else:
            st.info("Select a farmer to view their moisture trend.")
