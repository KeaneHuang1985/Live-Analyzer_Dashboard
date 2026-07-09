import streamlit as st
import pandas as pd
import plotly.express as px

def render_event_overview(dl_df):
    if dl_df.empty:
        st.info("No Receive Event Data...")
        return
    # =========================
    # Register DL FAILED SECTION
    # =========================
    st.divider()
    st.subheader("Event Overview")

    total_events = len(dl_df)
    dl_failed_count = len(dl_df[dl_df["event"] == "DL_FAILED"])
    deregister_count = len(dl_df[dl_df["event"] == "Deregister"])
    c1, c2, c3 = st.columns(3)
    c1.metric("BS Events", total_events)
    c2.metric("Register DL FAILED", dl_failed_count)
    c3.metric("Deregister", deregister_count)

    # =====================================
    # BS Event per ED
    # =====================================
    #st.subheader("BS Event Count per ED")
    #event_rank = (
    #    dl_df.groupby("ed_id")
    #    .size()
    #    .reset_index(name="event_count")
    #    .sort_values("event_count", ascending=False)
    #)
    #fig_fail = px.bar(
    #    event_rank,
    #    x="ed_id",
    #    y="event_count",
    #    color="event_count",
    #    title="BS Event Count per ED"
    #)
    #fig_fail.update_xaxes(type="category")
    #fig_fail.update_yaxes(tickformat="d")
    #st.plotly_chart(fig_fail,
    #                #use_container_width=True
    #                )

    # =====================================
    # DL_FAILED Reason
    # =====================================
    dl_failed_df = dl_df[
        dl_df["event"] == "DL_FAILED"
    ]
    if not dl_failed_df.empty:
        st.subheader("Register DL_FAILED Reason Count")
        reason_df = (
            dl_failed_df
            .groupby(["reason", "reason_code"])
            .size()
            .reset_index(name="count")
            .sort_values("count", ascending=False)
        )
        fig_reason = px.bar(
            reason_df,
            x="reason",
            y="count",
            color="count",
            hover_data=["reason_code"],
            title="Register Failure Reason Distribution"
        )
        st.plotly_chart(fig_reason)
        st.dataframe(reason_df)

    # =====================================
    # Deregister Reason
    # =====================================
    dereg_df = dl_df[dl_df["event"] == "Deregister"]
    if not dereg_df.empty:
        st.subheader("Deregister Reason Count")
        dereg_reason_df = (
            dereg_df
            .groupby(["reason", "reason_code"])
            .size()
            .reset_index(name="count")
            .sort_values("count", ascending=False)
        )
        st.dataframe(dereg_reason_df)

    # =====================================
    # Recent Events
    # =====================================
    st.subheader("Recent BS Events")
    st.dataframe(dl_df.sort_values("timestamp",ascending=False).head(100))

    # =====================================
    # Burst Detection
    # =====================================
    recent_5m = dl_df[dl_df["timestamp"] >pd.Timestamp.now() - pd.Timedelta(minutes=5)]
    if len(recent_5m) > 20:
        st.error(f"🚨 BS EVENT BURST ({len(recent_5m)} events / 5min)")
