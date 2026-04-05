import streamlit as st
from datetime import datetime

try:
    from handler import EndpointHandler
except Exception as e:
    EndpointHandler = None
    handler_error = str(e)
else:
    handler_error = None

st.set_page_config(page_title="BARROT-Ω", page_icon="🦾", layout="wide")
st.title("🦾 BARROT-Ω")
st.caption("Multi-Synchronous Relativistic Perception")

@st.cache_resource
def get_handler():
    if EndpointHandler is None:
        raise RuntimeError(handler_error)
    return EndpointHandler()

if EndpointHandler is None:
    st.error(f"Handler failed to load: {handler_error}")
else:
    h = get_handler()
    tab1, tab2 = st.tabs(["Status", "MRP"])

    with tab1:
        st.header("System Status")
        st.write("Timestamp:", datetime.utcnow().isoformat() + "Z")
        result = h({"inputs": "status", "parameters": {"backend": "mrp"}})
        st.json(result)

    with tab2:
        st.header("MRP Engine")
        query = st.text_input("Query", "sovereign status")
        backend = st.selectbox("Backend", ["gemma4", "qwen_vl", "mrp"], index=0)

        if st.button("Execute"):
            result = h({
                "inputs": query,
                "parameters": {"backend": backend}
            })
            st.json(result)
