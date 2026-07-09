import streamlit as st
import pandas as pd
from core.data_center import get_global_data
from core.render_helper import render_if_changed
from modules.ed_status import render_summary
data_center = get_global_data()

st.set_page_config(page_title="02_Connection_Count",layout="wide")
st.title("Connection_Count")


@st.fragment(run_every='8s')
def fragment_summary():
    df_raw = pd.DataFrame(data_center.get_max_ra_alloc_list())
    if render_if_changed(df_raw,"last_max_ra_alloc") :
        render_summary(df_raw)
    else:
        print("Did not need update page 02_Connection_Count")

fragment_summary()
        