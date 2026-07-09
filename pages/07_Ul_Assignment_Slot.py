import streamlit as st
import pandas as pd
from modules.ul_assignment import render_ul_assignment_dashboard  
from core.render_helper import render_if_changed
from core.data_center import get_global_data

data_center = get_global_data()
st.set_page_config(page_title="07_ul_assignment",layout="wide")
st.title("Ul Ra Assignment Slot")

@st.fragment(run_every="8s")
def fragment_ul_assignment_dashboard():
    df_raw = pd.DataFrame(data_center.get_ul_assignment_vals())
    if not df_raw.empty and render_if_changed(df_raw,'last_ul_assignment_vals'):
        render_ul_assignment_dashboard(df_raw)
    else:
        print("Did not need update page 07_Ul_Assignment_Slot")

fragment_ul_assignment_dashboard()