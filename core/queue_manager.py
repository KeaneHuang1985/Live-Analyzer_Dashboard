import queue
import streamlit as st

@st.cache_resource
def get_global_queue():
    return queue.Queue()