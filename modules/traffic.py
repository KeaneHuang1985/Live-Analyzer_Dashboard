import streamlit as st
import pandas as pd
import plotly.express as px

def render_rraffic_dashboard(latest):
    tab1, tab2 ,tab3= st.tabs(["Traffic Overview","UL Traffic","DL Traffic"]) 
    with tab1:
        render_traffic_overview(latest)
    with tab2:
        render_ul_rraffic(latest)
    with tab3:
        render_dl_rraffic(latest)



def render_ul_rraffic(latest):
    st.subheader("UL Traffic")
    tab1, tab2 = st.tabs(["Total UL Bytes", "Session UL Bytes"])
    with tab1:
        if "total_ul_rx_bytes" in latest.columns:
            fig_ul_total = px.bar(latest.sort_values("total_ul_rx_bytes", ascending=False),
                x="ed_id",
                y="total_ul_rx_bytes",
                color="status",
                title="Total Uplink Traffic per ED",
                labels={"ed_id": "ED ID","total_ul_rx_bytes": "Bytes"}
            )
            st.plotly_chart(fig_ul_total)

    with tab2:
        if "ul_rx_bytes" in latest.columns:
            fig_ul_session = px.bar(
                latest.sort_values("ul_rx_bytes", ascending=False),
                x="ed_id",
                y="ul_rx_bytes",
                color="status",
                title="Current Session Uplink Traffic per ED",
                labels={"ed_id": "ED ID","ul_rx_bytes": "Bytes"}
            )
            st.plotly_chart(fig_ul_session)

def render_dl_rraffic(latest):
    st.subheader("DL Traffic")
    tab1, tab2 = st.tabs(["Total DL Bytes","Session DL Bytes"])
    with tab1:
        if "total_dl_tx_bytes" in latest.columns:
            fig_ul_total = px.bar(latest.sort_values("total_dl_tx_bytes", ascending=False),
                x="ed_id",y="total_dl_tx_bytes",color="status",
                title="Total Uplink Traffic per ED",
                labels={"ed_id": "ED ID","total_dl_tx_bytes": "Bytes"}
            )
            st.plotly_chart(fig_ul_total)
    with tab2:
        if "dl_tx_bytes" in latest.columns:
            fig_ul_session = px.bar(
                latest.sort_values("dl_tx_bytes", ascending=False),
                x="ed_id",y="dl_tx_bytes",color="status",
                title="Current Session Donwlink Traffic per ED",
                labels={"ed_id": "ED ID","dl_tx_bytes": "Bytes"}
            )
            st.plotly_chart(fig_ul_session)

def render_traffic_overview(latest):
    total_ed = len(latest)
    st.subheader("Traffic Overview")
    total_ul = latest.get("total_ul_rx_bytes", pd.Series([0])).sum()
    total_dl = latest.get("total_dl_tx_bytes", pd.Series([0])).sum()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Active ED", total_ed)
    c2.metric("Total UL Bytes", format_bytes(total_ul))
    c3.metric("Total DL Bytes", format_bytes(total_dl))
    # when dl bytes is 0 byte Ratio is N/A
    if(total_dl > 0):
        c4.metric("UL/DL Ratio", round(total_ul / (total_dl + 1e-9), 2))
    else:
        c4.metric("UL/DL Ratio", "N/A (total_dl is 0 byte)")
    st.divider()

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