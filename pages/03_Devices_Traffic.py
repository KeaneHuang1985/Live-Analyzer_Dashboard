import streamlit as st
import pandas as pd
from core.data_center import get_global_data
from core.render_helper import render_if_changed
from modules.ed_status import render_ed_traffic_dashboard
from core.helper import add_status
data_center = get_global_data()

st.set_page_config(page_title="03_Devices_Traffic",layout="wide")
st.title("Devices Traffic & Keep Connection Time")

@st.fragment(run_every="10s")
def fragment_ed_traffic_dashboard():
    ed_status = data_center.get_ed_status_df()
    if render_if_changed(ed_status,'last_ed_status_df'):
        latest = ed_status.loc[ed_status.groupby("ed_id")["timestamp"].idxmax()].copy()
        latest = latest.drop_duplicates(subset=["ed_id"])
        latest = add_status(latest)
        render_ed_traffic_dashboard(latest)
    else:
        print("Did not need update page 03_Devices_Traffic")

fragment_ed_traffic_dashboard()
        