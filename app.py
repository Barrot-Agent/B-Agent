import streamlit as st
from datetime import datetime

try:
    from handler import EndpointHandler
except Exception as e:
    EndpointHandler = None
    handler_error = str(e)

st.set_page_config(page_title="BARROT-Ω", page_icon="🦾", layout="wide")

st.title("🦾 BARROT-Ω")
st.caption("Multi-Synchronous Relativistic Perception")

if EndpointHandler is None:
    st.error(f"Handler failed to load: {handler_error}")
else:
    h = EndpointHandler()
    
    tab1, tab2 = st.tabs(["Status", "MRP"])
    
    with tab1:
        st.header("System Status")
        result = h({"inputs": "status"})
        st.json(result)
    
    with tab2:
        st.header("MRP Engine")
        query = st.text_input("Query", "sovereign status")
        if st.button("Execute"):
            result = h({"inputs": query, "parameters": {"backend": "gemma4"}})
            st.json(result)
