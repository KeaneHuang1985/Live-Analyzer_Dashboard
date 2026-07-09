import streamlit as st
from core.data_center import get_global_data
global_data = get_global_data()


st.set_page_config(page_title="01_Gateway_info",layout="wide")
st.title("Gateway_info")


@st.fragment(run_every='20s')
def fragment_gateway_info():
    gateway_info = global_data.get_gateway_info()
    if gateway_info:
        for uuid, info in gateway_info.items():
            with st.container(border=True): 
                st.markdown(f"📡 Base Station: `{info.get('uuid', 'Unknown')}`")
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.markdown(f"**Version**\n`v{info.get('version', 0)}`")
                with c2:
                    st.markdown(f"**RunTime**\n{info.get('runtime', 0)} Second")
                with c3:
                    st.markdown(f"**UPTIME**\n{info.get('uptime', 0)} Second")
        st.divider()
    else:
        st.info("Not yet Get VBS Information...")
        st.divider()

fragment_gateway_info()