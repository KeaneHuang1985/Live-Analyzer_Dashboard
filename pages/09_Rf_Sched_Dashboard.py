import streamlit as st
import pandas as pd
from core.data_center import get_global_data
from core.helper import bb_sched_to_df
from core.render_helper import render_if_changed
from modules.rf_sched import render_rf_sched_dashboard
data_center = get_global_data()

st.set_page_config(page_title="09_Rf_Sched_Dashboard",layout="wide")
st.title("Rf Sched Dashboard")

@st.fragment(run_every="8s")
def fragment_rf_sched():
    df_raw = bb_sched_to_df(data_center.get_bb_sched_list())
    if render_if_changed(df_raw,'last_bb_sched_list'):
        render_rf_sched_dashboard(df_raw)
    else:
        print("Did not need update page 09_Rf_Sched_Dashboard")

fragment_rf_sched()