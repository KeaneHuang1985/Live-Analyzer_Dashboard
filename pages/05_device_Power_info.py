import streamlit as st
import pandas as pd
from core.data_center import get_global_data
from core.render_helper import render_if_changed
from modules.power_control import render_power_control
data_center = get_global_data()

st.set_page_config(page_title="05_device_Power_info",layout="wide")
st.title("Device Power Info")

@st.fragment(run_every="5s")
def fragment_power_dashboard():
    df_raw = pd.DataFrame(data_center.get_pwr_status_vals())
    if render_if_changed(df_raw,'last_pwr_status_vals'):
        render_power_control(df_raw)
    else:
        print("Did not need update page 05_device_Power_info")

fragment_power_dashboard()