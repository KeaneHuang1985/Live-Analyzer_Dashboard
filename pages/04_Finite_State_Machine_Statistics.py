import streamlit as st
import pandas as pd
from core.data_center import get_global_data
from core.render_helper import render_if_changed
from modules.GCT_Finite_State_Machine import render_fsm_statistics
from modules.phy_rx_req import render_phy_rx_req


global_data = get_global_data()
st.set_page_config(page_title="03_Finite_State_Machine_Statistics",layout="wide")
st.title("Finite State Machine Statistics")


@st.fragment(run_every="8s")
def fragment_fsm_statistics():
    df_raw = pd.DataFrame(global_data.get_fsm_list())
    if render_if_changed(df_raw,"last_fsm_list"):
        render_fsm_statistics(df_raw)
    else:
        print("Did not need update page 04_Finite_State_Machine_Statistics")

    phy_rx_req = global_data.get_phy_rx_req()
    if phy_rx_req:
        render_phy_rx_req(phy_rx_req)
    
fragment_fsm_statistics()