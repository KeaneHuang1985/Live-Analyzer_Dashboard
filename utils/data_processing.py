import streamlit as st
import pandas as pd

@st.cache_data(ttl=60)
def process_heavy_data(raw_data):
    df = pd.DataFrame(raw_data)
    return df