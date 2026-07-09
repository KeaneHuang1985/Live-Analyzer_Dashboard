import streamlit as st
import pandas as pd

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