import streamlit as st
import pandas as pd

def render_ll_lch_stats(df_raw: pd.DataFrame):
    st.subheader("📡[LCH Type Link quality diagnosis]")

    if df_raw.empty:
        st.info("No data...")
        return

    processed_rows = []
    for _, row in df_raw.iterrows():
        tx_cnt = int(row.get('tx_cnt', 0))
        retx_cnt = int(row.get('retx_cnt', 0))
        rx_cnt = int(row.get('rx_cnt', 0))
        lch_type = row.get('lch_type', 'UNKNOWN')
        ed_id = row.get('ed_id', 'UNKNOWN')
        
        # Calculate the success rate of sending
        total_tx = tx_cnt + retx_cnt
        success_rate = 100.0 if total_tx == 0 else round((tx_cnt / total_tx) * 100, 1)
        
        # Determine health indicator
        status_level = "GREEN"
        status_text = "🟢 Normal status"
        
        if lch_type == "LCH_UAC":
            if success_rate < 85.0:
                status_level, status_text = "RED", "🔴 Severe interruption (Control Drop)"
            elif success_rate < 95.0:
                status_level, status_text = "YELLOW", "🟡 Unstable (Control Retx)"
        elif lch_type == "LCH_UAD":
            if success_rate < 50.0:
                status_level, status_text = "RED", "🔴 Severe packet loss (Data Drop)"
            elif success_rate < 80.0:
                status_level, status_text = "YELLOW", "🟡 slight interference (Data Congest)"

        processed_rows.append({
            "ED ID": ed_id,
            "Channel": lch_type,
            "Status": status_text,
            "Level": status_level,
            "Success Rate (%)": success_rate,
            "TX Cnt": tx_cnt,
            "RETX Cnt": retx_cnt,
            "RX Cnt": rx_cnt,
            "TX Byte": int(row.get('tx_byte', 0)),
            "RETX Byte": int(row.get('retx_byte', 0)),
            "RX Byte": int(row.get('rx_byte', 0)),
            "Timestamp": row.get('timestamp')
        })

    df_ui = pd.DataFrame(processed_rows)

    # ---------------------------------------------------------
    # UI Presentation: Block A - High-Risk Alert Card (Conclusion First)
    # ---------------------------------------------------------
    # Find out which ED IDs contain the RED or YELLOW status.
    alert_ed_ids = df_ui[df_ui["Level"].isin(["RED", "YELLOW"])]["ED ID"].unique()
    """
    if len(alert_ed_ids) > 0:
        st.markdown("### ⚠️ Real-time alarm for abnormal devices")
        
        #Traversing the EDs that went wrong
        for ed in alert_ed_ids:
            with st.container(border=True):
                st.markdown(f"#### 📱 ED: `{ed}`")
                
                # Retrieve all channel data (UAC, UAD) for this ED
                ed_data = df_ui[df_ui["ED ID"] == ed]
                
                # Presented using a tree structure
                for _, ch_row in ed_data.iterrows():
                    ch = ch_row["Channel"]
                    status = ch_row["Status"]
                    rate = ch_row["Success Rate (%)"]
                    details = f"Success rate: **{rate}%** | TX: {ch_row['TX Cnt']} / RETX: {ch_row['RETX Cnt']} | RX: {ch_row['RX Cnt']} Pkts"
                    
                    if ch_row["Level"] == "RED":
                        st.markdown(f"**└── [{ch}] {status}**")
                        st.error(f"   ↳ 🚨 {details}")
                    elif ch_row["Level"] == "YELLOW":
                        st.markdown(f"**└── [{ch}] {status}**")
                        st.warning(f"   ↳ ⚠️ {details}")
                    else:
                        st.markdown(f"└── [{ch}] {status}")
                        st.caption(f"   ↳ {details}")
    else:
        st.success("🎉 Currently, the LCH link quality across the entire network is perfect, with no abnormal devices.。")
    st.divider()
    """

    # ---------------------------------------------------------
    # UI Presentation: Block B - Overview table of all ED statuses
    # ---------------------------------------------------------
    st.markdown("### 📊 Overview of all LCH statuses")
    
    # Sidebar or top filtering options (Optional: can be displayed directly
    # but here we use multiselect to allow users to filter)
    all_statuses = df_ui["Status"].unique()
    selected_statuses = st.multiselect("Filter channel status", all_statuses, default=all_statuses)
    
    df_filtered = df_ui[df_ui["Status"].isin(selected_statuses)]

    # 漂亮的表格欄位配置
    st.dataframe(
        df_filtered[["ED ID", "Channel", "Status", "Success Rate (%)", "TX Cnt", "RETX Cnt", "RX Cnt", "Timestamp"]],
        column_config={
            "Success Rate (%)": st.column_config.ProgressColumn(
                "Success rate of sending",
                help="Calculation formula: TX / (TX + RETX)",
                format="%f%%",
                min_value=0,
                max_value=100,
            ),
            "Timestamp": st.column_config.DatetimeColumn("Update time", format="YYYY-MM-DD HH:mm:ss.SS"),
        },
        hide_index=True,)
    

def render_tx_window_status_snapshot(fsm_df : pd.DataFrame, alarm_eds : list):
    st.markdown("---")
    st.markdown("## 🔄 LCH Serial Number state machine monitoring")
    if alarm_eds:
        st.error(f"🚨 **Major anomaly alarm ** : ED id : {alarm_eds}  ACK/NACK SN consecutively exceed the boundaries of the sliding window! `ll_lch_handle_invalid_bpd`。")
    st.dataframe(fsm_df,hide_index=True)
   