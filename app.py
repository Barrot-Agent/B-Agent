from __future__ import annotations

import streamlit as st

from barrot_agent.config import get_config
from barrot_agent.core import BAgent
from barrot_agent.models import ModelManager
from barrot_agent.smart_agent import AgentEventType, SmartAgent

st.set_page_config(page_title="B-Agent", page_icon="🦜", layout="wide")

config = get_config()
agent = BAgent(config=config)
model_manager = ModelManager(config=config.model)
smart_agent = SmartAgent()

st.title("B-Agent")
st.caption("Repository-local demo for the restored Barrot agent package.")

left, right = st.columns([2, 1])

with left:
    st.subheader("SmartAgent demo")
    goal = st.text_area(
        "Goal",
        value="Summarize the repository's current purpose and capabilities.",
        height=140,
    )

    btn_run, btn_reconfig = st.columns([1, 1])

    with btn_run:
        run_clicked = st.button("Run SmartAgent", type="primary")

    with btn_reconfig:
        reconfig_clicked = st.button(
            "🔧 Reconfigure Infrastructure",
            help=(
                "Run the SmartAgent reconfiguration loop: audit capability gaps, "
                "reason about improvements, and produce a structured reconfiguration plan."
            ),
        )

    if reconfig_clicked:
        reconfig_goal = (
            "Reconfigure Barrot's infrastructure to maximize capability coverage and minimize risk"
        )
        st.info(f"**Reconfiguration goal:** {reconfig_goal}")
        with st.status("Running infrastructure reconfiguration…", expanded=True) as status:
            events = []
            for event in smart_agent.run(reconfig_goal):
                events.append(event)
                if event.type == AgentEventType.THINKING:
                    st.write(f"💭 {event.content}")
                elif event.type == AgentEventType.PLAN:
                    st.write(f"📋 {event.content}")
                elif event.type == AgentEventType.ACTION:
                    st.write(f"⚡ {event.content}")
                elif event.type == AgentEventType.TOOL_RESULT:
                    with st.expander("Tool result", expanded=False):
                        st.markdown(event.content)
                elif event.type == AgentEventType.OBSERVATION:
                    st.write(f"🔎 {event.content}")
                elif event.type in (AgentEventType.ANSWER, AgentEventType.ERROR):
                    break
            final_event_is_error = events and events[-1].type == AgentEventType.ERROR
            if final_event_is_error:
                status.update(label="Reconfiguration failed.", state="error")
            else:
                status.update(label="Reconfiguration complete.", state="complete")
        final = next((e for e in reversed(events) if e.type == AgentEventType.ANSWER), None)
        if final is not None:
            st.subheader("📊 Reconfiguration Report")
            st.markdown(final.content)
        else:
            error = next((e for e in reversed(events) if e.type == AgentEventType.ERROR), None)
            st.error(error.content if error is not None else "No terminal event produced.")

    if run_clicked:
        events = list(smart_agent.run(goal))
        final = next(
            (event for event in reversed(events) if event.type == AgentEventType.ANSWER), None
        )
        if final is not None:
            st.markdown(final.content)
        else:
            error = next(
                (event for event in reversed(events) if event.type == AgentEventType.ERROR), None
            )
            st.error(error.content if error is not None else "No terminal event produced.")

with right:
    st.subheader("Runtime")
    st.json(
        {
            "app_version": agent.get_version(),
            "environment": str(config.environment),
            "debug": agent.is_debug(),
            "model_id": agent.get_model_id(),
            "model_loaded": model_manager.is_loaded,
        }
    )
    st.subheader("Granite metadata")
    st.json(model_manager.get_metadata())
