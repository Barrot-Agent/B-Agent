#!/usr/bin/env python3
import json
from pathlib import Path
import streamlit as st
from barrot_core import BarrotOmega

st.set_page_config(page_title="Barrot-Omega", layout="wide")

if "health" in dict(st.query_params):
    st.write("OK")
    st.stop()

if "agent" not in st.session_state:
    st.session_state.agent = BarrotOmega()
agent = st.session_state.agent

def read_jsonl_tail(path: Path, limit=20):
    if not path.exists(): return []
    out = []
    for raw in path.read_text(encoding="utf-8").splitlines()[-limit:]:
        raw = raw.strip()
        if raw:
            try: out.append(json.loads(raw))
            except: out.append({"raw": raw})
    return out

st.title("🦾 Barrot-Omega")
c1,c2,c3=st.columns(3)
with c1: 
    if st.button("Reconcile"): 
        agent.reconcile()
        st.success("Reconciled")
with c2:
    if st.button("Reload"): st.rerun()
with c3:
    st.metric("Status", agent.state.get("status", "unknown"))
    
tab1,tab2,tab3=st.tabs(["Directives","State","Logs"])

with tab1:
    directive=st.text_area("Directive",height=180)
    if st.button("Ingest",type="primary"):
        agent.ingest_directive(directive)
        agent.reconcile()
        st.success("Ingested")
    
    recent=read_jsonl_tail(agent.paths.directives_file,15)
    if recent:
        for item in reversed(recent): st.json(item)

with tab2:
    st.json(agent.state)
    files=f"""root: {agent.paths.root}
state_file: {agent.paths.state_file}
directives_file: {agent.paths.directives_file}
refine_log: {agent.paths.refine_log}
live_file: {agent.paths.live_file}
summary_file: {agent.paths.summary_file}"""
    st.code(files)

with tab3:
    logs=read_jsonl_tail(agent.paths.refine_log,25)
    if logs:
        for item in reversed(logs): st.json(item)
    else:
        st.info("No logs")
