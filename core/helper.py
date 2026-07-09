import pandas as pd
import streamlit as st

# =========================
# Data Helper Functions
# =========================
def add_status(df, offline_threshold=900):
    if df.empty:
        return df
    try:
        now = pd.Timestamp.now().tz_localize(None)
        last_seen = df.groupby("ed_id")["timestamp"].max().reset_index()
        last_seen["offline_sec"] = (now - last_seen["timestamp"]).dt.total_seconds()
        df = df.drop(columns=["offline_sec", "status"], errors="ignore")
        df = df.merge(last_seen[["ed_id", "offline_sec"]], on="ed_id", how="left")
        df["status"] = df["offline_sec"].apply(lambda x: "OFFLINE" if pd.isna(x) or x > offline_threshold else "ONLINE")
    except Exception as e:
        print(f"add_status failed {e} : {df}")
    return df

def bb_sched_to_df(sched_list) -> pd.DataFrame:
    sched_df = pd.DataFrame(sched_list)
    if sched_df.empty:
        return sched_df
    sched_df["timestamp"] = pd.to_datetime(sched_df["timestamp"])
    numeric_cols = ["duration", "rssi", "rssi_ref", "ul_waste", "prio_cur", "prio_max", "sfn"]
    for col in numeric_cols:
        if col in sched_df.columns:
            sched_df[col] = pd.to_numeric(sched_df[col], errors="coerce")
    sched_df["delta_rssi"] = sched_df["rssi"] - sched_df["rssi_ref"]
    return sched_df

def tx_status_data(tx_fsm_snapshot):
    fsm_rows = []
    alarm_eds = []
    
    for ed_id, data in tx_fsm_snapshot.items():
        fsm_rows.append({
            "ED ID": ed_id,
            "Current state machine": data["state"],
            "Number of consecutive out-of-bounds": data["invalid_cnt"],
            "SFN": data["sfn"],
            "Lch_Type": data["lch_type"],
            "Dynamic context information": data["info"],
            "Last updated": data["timestamp"]
        })
        if data["state"] == "🔴 BPD_INVALID_ALARM":
            alarm_eds.append(ed_id)
            
    raw_fsm_df = pd.DataFrame(fsm_rows).sort_values(by="ED ID")
    latest_fsm_df = raw_fsm_df.loc[raw_fsm_df.groupby("ED ID")["Last updated"].idxmax()].copy()
    return latest_fsm_df , alarm_eds

def render_if_changed(df:pd.DataFrame, key:str) -> bool:
    bool_hash = False

    if key not in st.session_state:
        st.session_state[key] = None
        return bool_hash
    
    current_hash = pd.util.hash_pandas_object(df).sum()
    if current_hash != st.session_state[key]:
        st.session_state[key] = current_hash
        bool_hash = True
    print(f"{key} hash result :{bool_hash}")
    return bool_hash