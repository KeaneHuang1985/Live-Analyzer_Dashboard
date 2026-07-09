import streamlit as st
import pandas as pd
from core.data_center import get_global_data
from core.render_helper import render_if_changed
from modules.ll_lch_stats import render_ll_lch_stats
data_center = get_global_data()

st.set_page_config(page_title="06_LCH_Link_quality_diagnosis",layout="wide")
st.title("LCH_Link_quality_diagnosis")

@st.fragment(run_every="4s")
def fragment_ll_lch_stats():
    df_raw = pd.DataFrame(data_center.get_ll_lch_log_stats_vals())
    if not df_raw.empty and render_if_changed(df_raw,'last_ll_lch_log_stats_vals'):
        render_ll_lch_stats(df_raw)
    else:
        print("Did not need update page 06_LCH_Link_quality_diagnosis")

fragment_ll_lch_stats()