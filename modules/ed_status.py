import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

def render_summary(df: pd.DataFrame):
    if df.empty:
        st.warning(" No summary data is currently available.。")
        return
    latest_row = df.iloc[-1]

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric(label="Total Devices",value=int(latest_row.get('total', 0)))
    with c2:
        st.metric(label="Connected",value=int(latest_row.get('connected', 0)))
    with c3:
        st.metric(label="Pending ED Register",value=int(latest_row.get('pending', 0)))

    st.divider()

def render_ed_traffic_dashboard(latest):
    if latest.empty:
        st.info(" Awaiting data updates... ")
        return

    tab1, tab2, tab3 ,tab4,tab5 = st.tabs([
        "ED Status",
        "Top Talker",
        "Session connection by hours",
        "Session Age Distribution",
        "Connect Rate Distribution"
        ])
    
    with tab1:
        render_ed_status_table(latest)
    with tab2:
        render_top_talker(latest)
    with tab3:
        render_session_age(latest)
    with tab4:
        render_session_age_distribution(latest)
    with tab5:
        render_connect_rate_distribution(latest)     

def format_bytes(size_in_bytes):
    """Automatically convert bytes to the appropriate units (KB, MB, GB) and format the output."""
    size_in_bytes = float(size_in_bytes)
    for unit in ['Bytes', 'KB', 'MB', 'GB', 'TB']:
        if size_in_bytes < 1024.0:
            if unit == 'Bytes':
                return f"{int(size_in_bytes)} {unit}"
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024.0
    return f"{size_in_bytes:.2f} PB"

def render_ed_status_table(latest):
    st.subheader("ED Status Table")
    # search
    search_ed = st.text_input(" Search ED :")
    # dispaly Count
    rows = st.number_input(" DisPlay Device's Status Rows : ",min_value=1,max_value=2000,value=10,step=100)

    if "age_sec" in latest.columns and "ul_schedule_count" in latest.columns:
        latest["avg_ul_interval_sec"] = np.where(
            latest["ul_schedule_count"] > 0,
            latest["age_sec"] / latest["ul_schedule_count"],
            np.nan
        ).round(1)
    
    # ========================
    if ("ul_rx_count" in latest.columns and "age_sec" in latest.columns):
        latest["ul_rx_per_hour"] = np.where(
            latest["age_sec"] > 0,
            latest["ul_rx_count"] * 3600 / latest["age_sec"],
            0
        ).round(2)
    # ========================


    table_columns = [
        "ed_id",
        "uuid",
        "state",
        "status",
        "registered_count",
        "connected_count",
        "connect_rate",
        "age_sec",
        "join_schedule_count",
        "ul_schedule_count",
        "avg_ul_interval_sec",
        "ul_rx_count",
        "ul_rx_bytes",
        "dl_tx_count",
        "dl_tx_bytes",
        "total_ul_rx_count",
        "total_ul_rx_bytes",
        "total_dl_tx_count",
        "total_dl_tx_bytes",
        "ul_efficiency",
        "ul_rx_per_hour"
    ]

    available_cols = [
        c for c in table_columns
        if c in latest.columns
    ]

    table_df = latest[available_cols].copy()

    # search ED
    if search_ed:
        table_df = table_df[table_df["ed_id"].astype(str).str.contains(search_ed, case=False, na=False)]

    table_df = table_df.head(rows)
    #dynamic_height row count
    dynamic_height = min(max(len(table_df) * 35 + 40, 200), 3000)
    if not table_df.empty:
        st.dataframe(
            table_df,
            #use_container_width=True,
            height=dynamic_height,
            column_config={
                "connect_rate": st.column_config.ProgressColumn("Conn(%)",help="Conn / Reg",min_value=0,max_value=100,format="%.1f%%"),
                "ul_efficiency": st.column_config.ProgressColumn("UL Eff(%)",help="UL RX Count / UL Schedule Count",min_value=0,max_value=100,format="%.1f%%"),
                "registered_count": st.column_config.NumberColumn("Reg"),
                "connected_count": st.column_config.NumberColumn("Conn"),
                "age_sec": st.column_config.NumberColumn("Age(s)"),
                "join_schedule_count": st.column_config.NumberColumn("JoinSched"),
                "ul_schedule_count": st.column_config.NumberColumn("ULSched",help="Accumulated UL Schedule Count"),
                "ul_schedule_interval": st.column_config.NumberColumn("ULInt"),
                "ul_rx_count": st.column_config.NumberColumn("UL_RX_COUNT",help="ul_rx_count"),
                "ul_rx_bytes": st.column_config.NumberColumn("UL_RX_B",format="%d",help="bytes"),
                "dl_tx_count": st.column_config.NumberColumn("DL_TX_Cnt",help="dl_tx_count"),
                "dl_tx_bytes": st.column_config.NumberColumn("DL_TX_B",format="%d",help="bytes"),
                "total_ul_rx_count": st.column_config.NumberColumn("Tot_UL_RX_Cnt",help="total_ul_rx_count count"),
                "total_ul_rx_bytes": st.column_config.NumberColumn("Tot_UL_B",format="%d",help="bytes"),
                "total_dl_tx_count": st.column_config.NumberColumn("Tot_DL_TX_Cnt",help="total_dl_tx_count count"),
                "total_dl_tx_bytes": st.column_config.NumberColumn("Tot_DL_B",format="%d",help="bytes"),
                "avg_ul_interval_sec": st.column_config.NumberColumn("Avg_UL_Int(s)",help="Age(sec) / UL Schedule Count",format="%.1f"),
                "ul_rx_per_hour": st.column_config.NumberColumn("UL/hr",help="UL RX/hr = Average number of uplink packets received per hour during the current session.",format="%.2f"),
            }
        )


def add_status(df, offline_threshold=900):
    if df.empty:
        return df
    now = pd.Timestamp.now().tz_localize(None)
    last_seen = df.groupby("ed_id")["timestamp"].max().reset_index()
    last_seen["offline_sec"] = (now - last_seen["timestamp"]).dt.total_seconds()
    df = df.drop(columns=["offline_sec", "status"], errors="ignore")
    df = df.merge(last_seen[["ed_id", "offline_sec"]], on="ed_id", how="left")
    df["status"] = df["offline_sec"].apply(lambda x: "OFFLINE" if pd.isna(x) or x > offline_threshold else "ONLINE")
    return df

def render_ed_detail_status_table(latest):
    st.subheader("ED Status Table")
    # search
    search_ed = st.text_input(" Search ED :")
    # dispaly Count
    rows = st.number_input(" DisPlay Device's Status Rows : ",min_value=1,max_value=2000,value=10,step=100)
    table_columns = [
        "ed_id","uuid",
        "state","status",
        "registered_count","connected_count","connect_rate",
        "age_sec",
        "join_sched_count","join_sched_interval",
        "ul_sched_count","ul_sched_interval",
        "session_ul_count","session_ul_bytes",
        "session_dl_count","session_dl_bytes",
        "total_ul_count","total_ul_bytes",
        "total_dl_count","total_dl_bytes"
    ]

    available_cols = [
        c for c in table_columns
        if c in latest.columns
    ]
    table_df = latest[available_cols].copy()
    # search ED
    if search_ed:
        table_df = table_df[table_df["ed_id"].astype(str).str.contains(search_ed, case=False, na=False)]
    table_df = table_df.head(rows)
    #dynamic_height row count
    dynamic_height = min(max(len(table_df) * 35 + 40, 200), 3000)
    if not table_df.empty:
        st.dataframe(
            table_df,
            #use_container_width=True,
            height=dynamic_height,
            column_config={
                "connect_rate":st.column_config.ProgressColumn("Conn(%)",help="conn/Req",min_value=0,max_value=100,format="%.1f%%"),
                "registered_count":st.column_config.NumberColumn("Reg"),
                "connected_count": st.column_config.NumberColumn("Conn"),
                "age_sec":st.column_config.NumberColumn("Age(s)"),
                "session_ul_bytes":st.column_config.NumberColumn("ses_ul_b",format="%d"),
                "session_dl_bytes":st.column_config.NumberColumn("ses_dl_b",format="%d"),
                "total_ul_bytes":st.column_config.NumberColumn("Tol_UL_b",format="%d"),
                "total_dl_bytes":st.column_config.NumberColumn("Tol_DL_b",format="%d")
            }
        )

def add_session_age_hr(latest_df):
    if latest_df.empty:
        return latest_df
    if "age_sec" in latest_df.columns:
        latest_df["session_age_hr"] = round(latest_df["age_sec"] / 3600, 2)
    else:
        latest_df["session_age_hr"] = 0.0     
    return latest_df

# render_session_age
def render_session_age(latest):
    if latest.empty:
        st.info("No data.")

    st.divider()
    st.subheader("Session connection by hours")
    latest = add_session_age_hr(latest)
    if "session_age_hr" in latest.columns:
        age_df_sorted = latest.sort_values("session_age_hr", ascending=False)
        fig_age = px.bar(
            age_df_sorted,
            x="ed_id",
            y="session_age_hr",
            labels={"session_age_hr": "Session Age (Hours)", "ed_id": "ed_id"},
            title="Active Session Duration per ED",
            text="session_age_hr",
            color="session_age_hr",
            color_continuous_scale="Viridis"
        )
        
        fig_age.update_traces(texttemplate='%{text}h', textposition='outside')
        fig_age.update_yaxes(title="Hours")
        
        st.plotly_chart(fig_age)
    else:
        st.info("No age_sec column found in data.")

def render_session_age_distribution(latest):
    if latest.empty:
        st.info("No data.")

    st.subheader("Session Connection time Distribution")
    age_bins = [-1, 1, 6, 12, 18, 24, 48, 72, 96, 120, 144, float("inf")]
    age_labels = [
        "low the 1 HR", "1~6 HR", "6~12 HR", "12 ~ 18 HR", "18 ~ 24HR", 
        "1 ~ 2 day", "2 ~ 3 day", "3 ~ 4 day", "4 ~ 5 day", "5 ~ 6 day", 
        "over the 6 day"
    ]
    latest["age_bin"] = pd.cut(latest["session_age_hr"],bins=age_bins,labels=age_labels)
    age_bin_df = (latest.groupby("age_bin", observed=False).size().reset_index(name="count"))
    fig_bin = px.bar(age_bin_df,x="age_bin",y="count",text="count",title="Devices by Session Age Bin")
    fig_bin.update_traces(textposition="outside")
    fig_bin.update_yaxes(title="Device Count")
    st.plotly_chart(fig_bin)
    st.dataframe(age_bin_df)

def render_connect_rate_distribution(latest):
    if latest.empty:
        st.info("No data.")

    if "connect_rate" in latest.columns:
        st.subheader("Connect Rate Distribution")

        fig2 = px.bar(
        latest.sort_values("connect_rate", ascending=False),
        x="ed_id",
        y="connect_rate",
        color="status",
        title="Connect Rate Distribution"
        )
        # GOOD
        fig2.add_hline(y=90,line_color="green",line_dash="dash",annotation_text="GOOD (90%)",annotation_font=dict(color="green", size=14),annotation_position="top left")
        # NORMAL
        fig2.add_hline(y=75,line_color="Yellow",line_dash="dash",annotation_text="NORMAL (75%)",annotation_font=dict(color="Yellow", size=14),annotation_position="top left")
        # BAD
        fig2.add_hline(y=50,line_color="Red",line_dash="dash",annotation_text="BAD (50%)",annotation_font=dict(color="Red", size=14),annotation_position="top left")
        fig2.update_yaxes(range=[0, 100],title="Connect Rate (%)",categoryorder='total ascending')
        st.plotly_chart(fig2)

def render_top_talker(latest):
    if latest.empty:
        st.info("No data.")

    st.subheader("Top Talker")
    if "total_ul_rx_bytes" in latest.columns:
        top_talker = latest.sort_values("total_ul_rx_bytes",ascending=False).head(15)
        st.dataframe(top_talker[["ed_id","connect_rate","total_ul_rx_bytes","total_dl_tx_bytes"]])
