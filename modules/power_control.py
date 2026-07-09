import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

def render_power_control(pwr_df):

    st.header("Power Control")
    if pwr_df.empty:
        st.info("No data...")
        return


    c1, c2, c3, c4 = st.columns(4)
    # 1. 總設備數
    total_ed = len(pwr_df)
    c1.metric("Total ED", total_ed)
    # 2. 平均鏈路功率
    c2.metric("Avg Link Power", round(pwr_df["link_pwr"].mean(), 1))
    # 3. Full Power 數量（等於或大於最大功率）
    full_power = (pwr_df["ul_tx_pwr"] >= pwr_df["max_tx_pwr"]).sum()
    c3.metric("Full Power Count", full_power)
    # 4. 非 Full Power 數量（嚴格小於最大功率）
    # 寫法 A：直接用總數減去 Full Power（最安全、效能最好）
    non_full_power = total_ed - full_power
    # 寫法 B：用條件式篩選小於 max_tx_pwr 的數量
    # non_full_power = (pwr_df["ul_tx_pwr"] < pwr_df["max_tx_pwr"]).sum()
    c4.metric("Non-Full Power Count", non_full_power)
    
    tab1, tab2, tab3 = st.tabs(["Current Status", "Worst Link Power", "Rssi Distribution"])
    with tab1:
        st.dataframe(pwr_df, width="stretch")
    with tab2:
        worst_df = pwr_df.nsmallest(20, "link_pwr")
        fig = px.bar(worst_df, x="ed_id", y="link_pwr")
        st.plotly_chart(fig, width="stretch", key="power_worst")
    with tab3:
        fig = px.histogram(pwr_df, x="link_pwr")
        st.plotly_chart(fig, width="stretch", key="power_dist")

def render_pwr_status_distribution(latest_df, events_df):
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Overview", "Power Distribution", "Link Analysis", "Correlation", "Events"
    ])

    if latest_df is None:
        latest_df = pd.DataFrame()
    if events_df is None:
        events_df = pd.DataFrame()

    with tab1:
        st.subheader("KPI")
        if latest_df.empty:
            st.info("No data")
        else:
            total = len(latest_df)
            maxed = (latest_df["ul_tx_pwr"] >= latest_df["max_tx_pwr"]).sum()
            weak = (latest_df["link_pwr_new"] < -100).sum()
            health = (latest_df["status"].isin(["BASIC", "RRM_STABLE"]).sum() / total * 100 if total else 0)
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total ED", total)
            c2.metric("Max Power", maxed)
            c3.metric("Weak Link", weak)
            c4.metric("Health %",f"{health:.1f}%",help="""
            Percentage of healthy devices.
            Formula:
            Health % = (Healthy Devices / Total Devices) × 100
            Healthy Devices:
            • BASIC
            • RRM_STABLE
            Example:
            80 healthy devices out of 100 total devices
            → Health % = 80%
            """
            )
            st.divider()
            status_df = latest_df["status"].value_counts().reset_index()
            status_df.columns = ["status", "count"]
            fig = px.bar(status_df, x="status", y="count", color="status")
            st.plotly_chart(fig)

    with tab2:
        st.subheader("NB_UL_RSSI Power Distribution (1/2)")
        if latest_df.empty:
            st.info("No data")
        else:
            latest_df = latest_df.copy()
            latest_df["nb_ul_rssi"] = pd.to_numeric(latest_df["nb_ul_rssi"], errors="coerce")
            rssi_th = -110
            latest_df["rssi_state"] = np.where(latest_df["nb_ul_rssi"].notna() & (latest_df["nb_ul_rssi"] < rssi_th), "WEAK", "GOOD")
            fig = px.histogram(latest_df, x="nb_ul_rssi", nbins=20, color="rssi_state")
            fig.add_vline(x=rssi_th, line_dash="dash", line_color="red")
            st.plotly_chart(fig)
            
            st.subheader("Box View by Status (2/2)")
            fig2 = px.box(latest_df, x="status", y="nb_ul_rssi", color="status")
            st.plotly_chart(fig2)

    with tab3:
        if events_df.empty and latest_df.empty:
            st.info(f"Can't render: events_df count is {len(events_df)}, latest_df count is {len(latest_df)}")
        else:
            # fig 1
            st.subheader("Link Power Distribution (1/2)")
            if not latest_df.empty:
                fig = px.histogram(latest_df, x="link_pwr_new", nbins=30)
                fig.add_vline(x=-110, line_dash="dash", line_color="red")
                st.plotly_chart(fig)
            else:
                st.info("No latest link data to display histogram")

            # fig 2
            rows = st.number_input("Top N EDs", min_value=1, max_value=1000, value=5, step=5)
            st.subheader("Top EDs Link Power Trend (2/2)")
            
            # 【已修正】移除原本的 st.session_state 讀取，直接使用外部傳入的 events_df 快照
            if not events_df.empty:
                top_eds = events_df["ed_id"].value_counts().head(rows).index
                fig2 = px.line(events_df[events_df["ed_id"].isin(top_eds)], x="timestamp", y="link_pwr_new", color="ed_id")
                st.plotly_chart(fig2)
            else:
                st.info("No trend data available (events_df is empty)")

    with tab4:
        st.subheader("UL Power vs Link Power")
        if latest_df.empty:
            st.info("No data")
        else:
            fig = px.scatter(latest_df, x="link_pwr_new", y="ul_tx_pwr", color="status", hover_data=["ed_id"])
            fig.add_hline(y=27, line_dash="dash", line_color="red")
            fig.add_vline(x=-100, line_dash="dash", line_color="red")
            st.plotly_chart(fig)

    with tab5:
        st.subheader("Power Control Events")
        if events_df.empty:
            st.info("No events yet")
        else:
            rows = st.number_input("Display Events Rows :", min_value=1, max_value=2000, value=10, step=100)
            sorted_df = events_df.sort_values("timestamp", ascending=False)
            st.dataframe(sorted_df.head(rows), width="stretch")