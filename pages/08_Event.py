import streamlit as st
import pandas as pd
from modules.event import render_event_overview
from core.render_helper import render_if_changed
from core.data_center import get_global_data
data_center = get_global_data()

st.set_page_config(page_title="08_Event",layout="wide")
st.title("Register or Disconnected Event")


@st.fragment(run_every="8s")
def fragment_event_overview():
    df_raw = pd.DataFrame(data_center.get_dl_failures())
    if render_if_changed(df_raw,'last_dl_failures'):
        render_event_overview(df_raw)
    else:
        print("Did not need update page 08_Event")

fragment_event_overview()