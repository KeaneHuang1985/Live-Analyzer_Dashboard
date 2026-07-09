import streamlit as st

# ==============================================
# Core
from core.websocket import init_background_threads
#from core.data_center import GlobalDataCenter
# ==============================================
# UI page 
#from pages.ed import fragment_summary
#from pages.Gateway import fragment_gateway_info
#from pages.Fsm_St_Stats import frament_fsm_statistics
# =========================
# Config
# =========================
init_background_threads()
#st.set_page_config(layout="wide",page_title="LilyBS RF Monitor")
#st.title("LilyBS RF Monitor")
#st.info("Please select a page from the sidebar.")



