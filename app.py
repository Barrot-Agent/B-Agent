import streamlit as st
from datetime import datetime

st.set_page_config(page_title="BARROT-Ω", page_icon="🦾", layout="wide")
st.title("🦾 BARROT-Ω")
st.caption("Minimal lazy-load control plane")

@st.cache_resource
def get_handler():
    from handler import EndpointHandler
    return EndpointHandler()

h = get_handler()

tab1, tab2 = st.tabs(["Status", "MRP"])

with tab1:
    st.header("System Status")
    st.write("Timestamp:", datetime.utcnow().isoformat() + "Z")
    st.json(h({"inputs": "status", "parameters": {"backend": "mrp"}}))

with tab2:
    st.header("MRP Engine")
    query = st.text_input("Query", "sovereign status")
    backend = st.selectbox("Backend", ["mrp", "gemma4", "qwen_vl"], index=0)

    if st.button("Execute"):
        with st.spinner(f"Running {backend}..."):
            st.json(h({
                "inputs": query,
                "parameters": {"backend": backend}
            }))
