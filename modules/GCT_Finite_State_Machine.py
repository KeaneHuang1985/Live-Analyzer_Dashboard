import streamlit as st
import pandas as pd

# =============================
#   ST status
# =============================
#   State = 0 (IDLE)
#   State = 1 (PRE0)
#   State = 2 (SFD0)
#   State = 3 (SFD1)
#   State = 4 (PAYLOAD)
# =============================


def render_fsm_statistics(fsm_df):
    st.header("Finite State Machine Statistics")
    if fsm_df.empty:
        st.info("No Finite State Machine Statistics data ...")
        return

    if 'timestamp' in fsm_df.columns:
        fsm_df['timestamp'] = pd.to_datetime(fsm_df['timestamp'])
        start_time = fsm_df['timestamp'].min().strftime('%Y-%m-%d %H:%M:%S')
        last_updated = fsm_df['timestamp'].max().strftime('%Y-%m-%d %H:%M:%S')
        
        st.caption(f"📅 ** Data Range: ** {start_time} ➔ {last_updated}")
    # --------------------------------------------
    tab1, tab2 = st.tabs(["NORMAL", "CA"])
    
    with tab1:
        st.dataframe(
            build_fsm_summary(fsm_df,"NORMAL"),
            width="stretch",
            column_config={
                    "Sync Failed Rate": st.column_config.ProgressColumn("Sync Failed Rate",min_value=0,max_value=100,format="%.2f%%",color="#FF4B4B"),
                    "Payload Lock Rate": st.column_config.ProgressColumn("Payload Lock Rate",min_value=0,max_value=100,format="%.2f%%",color="#0CB60CDF"),
                }
        )
    with tab2:
        st.dataframe(
            build_fsm_summary(fsm_df,"CA"),
            width="stretch",
            column_config={
                    "Sync Failed Rate": st.column_config.ProgressColumn("Sync Failed Rate",min_value=0,max_value=100,format="%.2f%%",color="#FF4B4B"),
                    "Payload Lock Rate": st.column_config.ProgressColumn("Payload Lock Rate",min_value=0,max_value=100,format="%.2f%%",color="#0CB60CDF"),
                },
        )

def build_fsm_summary(df, bpd_type):
    if df.empty:
        return pd.DataFrame()
    df = df[df["bpd_type"] == bpd_type]
    if df.empty:
        return pd.DataFrame()
    rows = []
    total_st0 = 0
    total_st1 = 0
    total_st2 = 0
    total_st3 = 0
    total_st4 = 0
    
    for ch in range(8):
        col = f"subchannel_{ch}"
        st0 = (df[col].astype(str) == "0").sum()
        st1 = (df[col].astype(str) == "1").sum()
        st2 = (df[col].astype(str) == "2").sum()
        st3 = (df[col].astype(str) == "3").sum()
        st4 = (df[col].astype(str) == "4").sum()
        total = st1 + st2 + st3 + st4

        total_st0 += st0
        total_st1 += st1
        total_st2 += st2
        total_st3 += st3
        total_st4 += st4

        rows.append({
            "CH": str(ch),
            "ST0": st0,
            "ST1": st1,
            "ST2": st2,
            "ST3": st3,
            "ST4": st4,
            "Sync Failed Rate": round(
                (st1 + st2 + st3) / total * 100, 2
            ) if total else 0,
            "Payload Lock Rate": round(
                st4 / total * 100, 2
            ) if total else 0,
        })
    grand_total = total_st1 + total_st2 + total_st3 + total_st4
    rows.append({
        "CH": "TOTAL",
        "ST0": total_st0,
        "ST1": total_st1,
        "ST2": total_st2,
        "ST3": total_st3,
        "ST4": total_st4,
        "Sync Failed Rate": round(
            (total_st1 + total_st2 + total_st3)
            / grand_total * 100, 2
        ) if grand_total else 0,
        "Payload Lock Rate": round(
            total_st4 / grand_total * 100, 2
        ) if grand_total else 0,
    })
    result = pd.DataFrame(rows)
    result["CH"] = result["CH"].astype(str)
    return result