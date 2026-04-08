"""
Barrot Agent – Streamlit Application
======================================
Main entry point.  Provides a tabbed interface with:
  • Home – agent status / torch diagnostic
  • Stupid Sindy Video Studio – 15-episode video production pipeline
  • Apex Lattice Analysis Pipeline – sandbox analysis and recommendations
  • AI Directive Platform – multi-agent collaboration driven by human directives
"""

import time
import streamlit as st

st.set_page_config(
    page_title="Barrot Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Lazy torch import (avoids blocking the whole app on startup)
# ---------------------------------------------------------------------------

@st.cache_resource(show_spinner=False)
def _load_torch():
    try:
        import torch  # noqa: F401
        return True, None
    except ImportError as exc:
        return False, str(exc)


# ---------------------------------------------------------------------------
# Imports that are always available
# ---------------------------------------------------------------------------

from stupid_sindy_series_generator import (  # noqa: E402
    get_all_characters,
    get_all_episodes,
    get_episode,
    episode_summary_card,
)
from sindy_video_pipeline import (  # noqa: E402
    SindyVideoPipeline,
    RenderStatus,
)
from apex_lattice import (  # noqa: E402
    CycleManager,
    AuditTrail,
    FindingGenerator,
    RecommendationEngine,
)
from directive_platform import (  # noqa: E402
    DirectivePlatform,
    DirectiveType,
    DirectiveStatus,
    AgentStatus,
    MessageType,
)

# ---------------------------------------------------------------------------
# Shared pipeline (cached across reruns)
# ---------------------------------------------------------------------------

@st.cache_resource(show_spinner=False)
def get_pipeline() -> SindyVideoPipeline:
    return SindyVideoPipeline()


# ===========================================================================
# Page: Home
# ===========================================================================

def page_home() -> None:
    st.title("🤖 Barrot Agent")
    st.markdown("Welcome to the Barrot Agent control panel.")

    with st.spinner("Checking torch…"):
        torch_ok, torch_err = _load_torch()

    col1, col2 = st.columns(2)
    with col1:
        if torch_ok:
            st.success("✅ PyTorch loaded successfully")
        else:
            st.warning(f"⚠️ PyTorch unavailable: {torch_err}")
    with col2:
        st.info("Navigate to **Stupid Sindy Video Studio** in the sidebar to generate episodes.")

    st.divider()
    st.markdown(
        """
### About Barrot Agent
Barrot is a self-improving agent infrastructure that combines:
- **Language understanding** via the Chi language server
- **Distributed inference** for large model serving
- **Sandbox analysis** via the Apex Lattice cascade system
- **Creative video production** via the Stupid Sindy pipeline

Select a page in the sidebar to get started.
        """
    )


# ===========================================================================
# Page: Stupid Sindy Video Studio
# ===========================================================================

_STATUS_EMOJI = {
    RenderStatus.QUEUED:    "⏳",
    RenderStatus.RENDERING: "🎬",
    RenderStatus.COMPLETE:  "✅",
    RenderStatus.ERROR:     "❌",
}

_STATUS_COLOUR = {
    RenderStatus.QUEUED:    "orange",
    RenderStatus.RENDERING: "blue",
    RenderStatus.COMPLETE:  "green",
    RenderStatus.ERROR:     "red",
}


def _episode_status_badge(pipeline: SindyVideoPipeline, ep_num: int) -> str:
    state = pipeline.get_state(ep_num)
    if state is None:
        return "⬜ Not generated"
    emoji = _STATUS_EMOJI.get(state.status, "❓")
    colour = _STATUS_COLOUR.get(state.status, "grey")
    label = state.status.value.title()
    return f":{colour}[{emoji} {label}]"


def _render_episode_card(ep_num: int, pipeline: SindyVideoPipeline) -> None:
    """Render a compact episode info card in a grid cell."""
    ep = get_episode(ep_num)
    card = episode_summary_card(ep)
    badge = _episode_status_badge(pipeline, ep_num)
    with st.container(border=True):
        st.markdown(f"**Ep {card['number']}: {card['title']}**")
        st.caption(f"{card['description']}")
        st.markdown(
            f"🕐 {card['runtime']} &nbsp;|&nbsp; "
            f"🎭 {card['cast']} &nbsp;|&nbsp; "
            f"🎬 {card['scenes']} scenes",
            unsafe_allow_html=True,
        )
        st.markdown(badge)


def page_sindy_studio() -> None:
    pipeline = get_pipeline()

    st.title("🎬 Stupid Sindy – Video Studio")
    st.markdown(
        "Browse all 15 episodes, generate individual episodes, "
        "view scripts, and play back rendered videos."
    )

    # -----------------------------------------------------------------------
    # Sidebar controls
    # -----------------------------------------------------------------------
    with st.sidebar:
        st.header("🎬 Episode Controls")
        selected_ep = st.selectbox(
            "Select Episode",
            options=list(range(1, 16)),
            format_func=lambda n: f"Ep {n}: {get_episode(n).title}",
            key="sindy_selected_ep",
        )

        st.divider()
        col_a, col_b = st.columns(2)
        with col_a:
            gen_btn = st.button("▶ Generate", use_container_width=True, type="primary")
        with col_b:
            reset_btn = st.button("🗑 Reset", use_container_width=True)

        if reset_btn:
            pipeline.reset_episode(selected_ep)
            st.rerun()

        st.divider()
        batch_btn = st.button("⚡ Batch Generate All", use_container_width=True)

        st.divider()
        st.markdown("**Series Status**")
        all_states = pipeline.all_states()
        complete = sum(1 for s in all_states.values() if s.status == RenderStatus.COMPLETE)
        rendering = sum(1 for s in all_states.values() if s.status == RenderStatus.RENDERING)
        queued = sum(1 for s in all_states.values() if s.status == RenderStatus.QUEUED)

        st.metric("✅ Complete", complete)
        st.metric("🎬 Rendering", rendering)
        st.metric("⏳ Queued", queued)
        st.metric("⬜ Not started", 15 - len(all_states))

    # -----------------------------------------------------------------------
    # Main content tabs
    # -----------------------------------------------------------------------
    tab_episodes, tab_player, tab_script, tab_characters = st.tabs(
        ["📋 Episodes", "▶ Video Player", "📄 Script", "🎭 Characters"]
    )

    # == Tab 1: Episodes ==
    with tab_episodes:
        st.subheader("All Episodes")
        episodes = get_all_episodes()
        cols = st.columns(3)
        for i, ep in enumerate(episodes):
            with cols[i % 3]:
                _render_episode_card(ep.episode_number, pipeline)

    # == Tab 2: Video Player ==
    with tab_player:
        ep = get_episode(selected_ep)
        st.subheader(f"Episode {selected_ep}: {ep.title}")
        st.markdown(f"> {ep.description}")

        state = pipeline.get_state(selected_ep)

        # Queue and render when Generate is clicked
        if gen_btn:
            if state is None or state.status not in (RenderStatus.RENDERING, RenderStatus.COMPLETE):
                pipeline.queue_episode(selected_ep)
                state = pipeline.get_state(selected_ep)

        # Run the render loop for any episode that is queued or freshly triggered
        if gen_btn and state is not None and state.status == RenderStatus.QUEUED:
            progress_bar = st.progress(0.0, text="Starting render…")
            status_text = st.empty()

            for update in pipeline.render_episode(selected_ep):
                pct = int(update.progress * 100)
                if update.status == RenderStatus.RENDERING:
                    scene_est = max(1, int(update.progress * len(ep.scenes)))
                    progress_bar.progress(
                        update.progress,
                        text=f"🎬 Rendering scene {scene_est}/{len(ep.scenes)} … {pct}%",
                    )
                    status_text.markdown(
                        f"**Status:** :blue[{update.status.value.title()}] "
                        f"| Progress: {pct}%"
                    )
                elif update.status == RenderStatus.COMPLETE:
                    progress_bar.progress(1.0, text="✅ Render complete!")
                    status_text.markdown("**Status:** :green[Complete]")
                elif update.status == RenderStatus.ERROR:
                    status_text.markdown(
                        f"**Status:** :red[Error] – {update.error_message}"
                    )
                    break

            st.rerun()

        # Show current state
        state = pipeline.get_state(selected_ep)
        if state is None:
            st.info("Click **▶ Generate** in the sidebar to render this episode.")
        elif state.status == RenderStatus.QUEUED:
            st.info("Episode is queued. Click **▶ Generate** to start rendering.")
        elif state.status == RenderStatus.COMPLETE:
            video_path = pipeline.get_video_path(selected_ep)
            if video_path:
                st.success("✅ Episode rendered successfully!")
                elapsed = (state.completed_at or 0) - (state.started_at or 0)
                st.caption(f"Rendered in {elapsed:.1f}s")
                with open(video_path, "rb") as vf:
                    st.video(vf.read(), format="video/mp4")
            else:
                st.warning("Video file not found. Click **🗑 Reset** and regenerate.")
        elif state.status == RenderStatus.ERROR:
            st.error(f"Render failed: {state.error_message}")
            st.info("Click **🗑 Reset** to clear and try again.")

    # == Tab 3: Script ==
    with tab_script:
        ep = get_episode(selected_ep)
        st.subheader(f"Script – Episode {selected_ep}: {ep.title}")

        col_meta, col_script = st.columns([1, 2])
        with col_meta:
            st.markdown(f"**Runtime:** {ep.runtime_minutes} min")
            st.markdown(f"**Cast:** {', '.join(ep.characters)}")
            st.markdown(f"**Scenes:** {len(ep.scenes)}")
            st.divider()
            st.markdown("**Scene List**")
            for scene in ep.scenes:
                st.markdown(f"- Scene {scene.scene_number}: *{scene.title}*")

        with col_script:
            st.text_area(
                "Full Script",
                value=ep.full_script(),
                height=500,
                key=f"script_{selected_ep}",
            )

    # == Tab 4: Characters ==
    with tab_characters:
        st.subheader("Series Characters")
        characters = get_all_characters()
        char_cols = st.columns(2)
        for i, (name, char) in enumerate(characters.items()):
            with char_cols[i % 2]:
                with st.container(border=True):
                    st.markdown(f"### {char.name}")
                    st.markdown(char.description)
                    st.markdown(f"*Catchphrase:* **\"{char.catchphrase}\"**")

    # -----------------------------------------------------------------------
    # Batch generate handler (runs outside tabs so it can own the screen)
    # -----------------------------------------------------------------------
    if batch_btn:
        st.divider()
        st.subheader("⚡ Batch Generating All Episodes")
        overall = st.progress(0.0, text="Queuing episodes…")
        episode_status = st.empty()

        for ep_num in range(1, 16):
            state = pipeline.get_state(ep_num)
            if state and state.status == RenderStatus.COMPLETE:
                overall.progress(ep_num / 15, text=f"Episode {ep_num} already complete – skipping")
                continue

            pipeline.queue_episode(ep_num)
            episode_status.markdown(f"🎬 **Rendering Episode {ep_num}…**")

            for update in pipeline.render_episode(ep_num):
                overall.progress(
                    ((ep_num - 1) + update.progress) / 15,
                    text=f"Episode {ep_num}/15 – {int(update.progress * 100)}%",
                )

        overall.progress(1.0, text="✅ All episodes rendered!")
        episode_status.markdown("**All 15 episodes have been generated.**")
        time.sleep(1)
        st.rerun()


# ===========================================================================
# Page: Apex Lattice Analysis Pipeline
# ===========================================================================

_SEVERITY_COLOUR = {
    "critical": "red",
    "high": "orange",
    "medium": "orange",
    "low": "blue",
    "info": "gray",
}


@st.cache_resource(show_spinner=False)
def get_cycle_manager() -> CycleManager:
    return CycleManager()


def page_apex_lattice() -> None:
    manager = get_cycle_manager()

    st.title("🔬 Apex Lattice — Sandbox Analysis Pipeline")
    st.markdown(
        "Processes data from the `.apex_lattice/` sandbox, identifies "
        "infrastructure improvement opportunities, and generates structured proposals."
    )

    # -----------------------------------------------------------------------
    # Sidebar controls
    # -----------------------------------------------------------------------
    with st.sidebar:
        st.header("🔬 Analysis Controls")
        run_btn = st.button("▶ Run Analysis Cycle", use_container_width=True, type="primary")
        st.divider()
        st.markdown("**Scheduler**")
        interval = st.number_input("Interval (seconds)", min_value=60, value=3600, step=60)
        col_start, col_stop = st.columns(2)
        with col_start:
            sched_start = st.button("▶ Start", use_container_width=True)
        with col_stop:
            sched_stop = st.button("⏹ Stop", use_container_width=True)

        if sched_start:
            manager.start_scheduler(float(interval))
            st.success("Scheduler started.")
        if sched_stop:
            manager.stop_scheduler()
            st.info("Scheduler stopped.")

        st.divider()
        scheduler_running = manager.is_scheduler_running()
        st.markdown(
            f"**Scheduler:** {'🟢 Running' if scheduler_running else '⚫ Stopped'}"
        )

    # -----------------------------------------------------------------------
    # Run cycle
    # -----------------------------------------------------------------------
    if run_btn:
        with st.spinner("Running analysis cycle…"):
            result = manager.run_cycle()
        if result.error:
            st.error(f"Cycle failed: {result.error}")
        else:
            st.success(
                f"✅ Cycle `{result.cycle_id}` complete in "
                f"{result.duration_seconds:.2f}s — "
                f"{len(result.artefacts)} artefacts, "
                f"{result.findings_count} findings, "
                f"{result.recommendations_count} recommendations."
            )
            if result.pr_document:
                st.info(f"PR document written to `{result.pr_document}`")
        st.rerun()

    # -----------------------------------------------------------------------
    # Tabs
    # -----------------------------------------------------------------------
    tab_findings, tab_recs, tab_audit = st.tabs(
        ["🔍 Findings", "💡 Recommendations", "📋 Audit Log"]
    )

    apex_dir = manager.apex_dir

    with tab_findings:
        st.subheader("Findings")
        gen = FindingGenerator(apex_dir / "findings")
        findings = gen.load_all()
        if not findings:
            st.info("No findings yet. Click **▶ Run Analysis Cycle** to generate them.")
        else:
            st.markdown(f"**{len(findings)} finding(s) on record.**")
            for f in findings:
                colour = _SEVERITY_COLOUR.get(f.severity, "gray")
                with st.container(border=True):
                    st.markdown(
                        f":{colour}[**{f.severity.upper()}**] "
                        f"`{f.category}` — **{f.title}**"
                    )
                    st.caption(f.description)

    with tab_recs:
        st.subheader("Recommendations")
        engine = RecommendationEngine(apex_dir / "recommendations")
        recs = engine.load_all()
        if not recs:
            st.info("No recommendations yet. Click **▶ Run Analysis Cycle** to generate them.")
        else:
            st.markdown(f"**{len(recs)} recommendation(s) on record.**")
            for rec in recs:
                colour = _SEVERITY_COLOUR.get(rec.priority, "gray")
                with st.expander(
                    f":{colour}[{rec.priority.upper()}] {rec.title}",
                    expanded=False,
                ):
                    st.markdown(f"**Rationale:** {rec.rationale}")
                    st.markdown("**Action Items:**")
                    for item in rec.action_items:
                        st.markdown(f"- {item}")

    with tab_audit:
        st.subheader("Audit Log")
        trail = AuditTrail(apex_dir / "audit_logs")
        events = trail.tail(50)
        if not events:
            st.info("No audit events yet.")
        else:
            import json as _json
            rows = []
            for ev in reversed(events):
                ts = ev.get("ts", 0)
                ts_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts))
                rows.append(
                    {
                        "Timestamp": ts_str,
                        "Event": ev.get("event", ""),
                        "Data": _json.dumps(ev.get("data", {})),
                    }
                )
            st.dataframe(rows, use_container_width=True)


# ===========================================================================
# Page: AI Directive Platform
# ===========================================================================

_DTYPE_COLOUR: dict[str, str] = {
    DirectiveType.LEARN:            "blue",
    DirectiveType.REFINE:           "orange",
    DirectiveType.ANALYZE:          "violet",
    DirectiveType.COOPERATE:        "green",
    DirectiveType.CROSS_CORROBORATE: "red",
    DirectiveType.PROJECT:          "gray",
}

_DSTATUS_COLOUR: dict[str, str] = {
    DirectiveStatus.PENDING:   "orange",
    DirectiveStatus.ACTIVE:    "blue",
    DirectiveStatus.COMPLETED: "green",
    DirectiveStatus.FAILED:    "red",
}

_MTYPE_EMOJI: dict[str, str] = {
    MessageType.DIRECTIVE: "📋",
    MessageType.RESPONSE:  "💬",
    MessageType.QUERY:     "❓",
    MessageType.INSIGHT:   "💡",
    MessageType.RESULT:    "✅",
    MessageType.HANDOFF:   "🔀",
}


@st.cache_resource(show_spinner=False)
def get_directive_platform() -> DirectivePlatform:
    return DirectivePlatform()


def _directive_badge(directive_type: str, status: str) -> str:
    dtype_colour = _DTYPE_COLOUR.get(directive_type, "gray")
    dstatus_colour = _DSTATUS_COLOUR.get(status, "gray")
    return (
        f":{dtype_colour}[{DirectiveType.label(directive_type)}] "
        f":{dstatus_colour}[{DirectiveStatus.label(status)}]"
    )


def page_directive_platform() -> None:
    platform = get_directive_platform()

    st.title("🤝 AI Directive Platform")
    st.markdown(
        "Issue directives to AI agents and watch them collaborate to fulfil your goals. "
        "Agents can learn, refine capabilities, analyze data, cooperate, "
        "cross-corroborate information, or work on projects together."
    )

    # -----------------------------------------------------------------------
    # Sidebar: quick stats
    # -----------------------------------------------------------------------
    with st.sidebar:
        st.header("📊 Platform Stats")
        all_agents = platform.registry.list_all()
        all_directives = platform.directives.list_all()
        all_sessions = platform.sessions.list_sessions()

        idle_count = sum(1 for a in all_agents if a.status == AgentStatus.IDLE)
        active_count = sum(1 for a in all_agents if a.status == AgentStatus.ACTIVE)
        st.metric("🤖 Agents", len(all_agents))
        st.metric("🟢 Idle", idle_count)
        st.metric("🔵 Active", active_count)
        st.divider()
        completed = sum(1 for d in all_directives if d.status == DirectiveStatus.COMPLETED)
        pending = sum(1 for d in all_directives if d.status == DirectiveStatus.PENDING)
        st.metric("📋 Total Directives", len(all_directives))
        st.metric("✅ Completed", completed)
        st.metric("⏳ Pending", pending)
        st.metric("💬 Sessions", len(all_sessions))

    # -----------------------------------------------------------------------
    # Tabs
    # -----------------------------------------------------------------------
    tab_new, tab_directives, tab_agents, tab_sessions = st.tabs(
        ["➕ New Directive", "📋 Directives", "🤖 Agents", "💬 Sessions"]
    )

    # =========== Tab: New Directive =========================================
    with tab_new:
        st.subheader("Issue a New Directive")
        st.markdown(
            "Fill in the form below to assign a collaborative task to one or "
            "more AI agents."
        )

        col_form, col_help = st.columns([2, 1])

        with col_form:
            human_author = st.text_input(
                "Your name (operator)",
                value="Operator",
                key="dp_author",
            )
            directive_title = st.text_input(
                "Directive title",
                placeholder="e.g. Learn about transformer attention mechanisms",
                key="dp_title",
            )
            directive_desc = st.text_area(
                "Directive description",
                placeholder=(
                    "Describe what you want the agents to accomplish in detail. "
                    "Include any constraints, preferred approaches, or expected "
                    "deliverables."
                ),
                height=120,
                key="dp_desc",
            )

            directive_type = st.selectbox(
                "Directive type",
                options=DirectiveType.ALL,
                format_func=DirectiveType.label,
                key="dp_type",
            )

            available_agents = platform.registry.list_all()
            agent_options = {a.agent_id: f"{a.name} — {', '.join(a.capabilities[:3])}" for a in available_agents}
            selected_agent_ids = st.multiselect(
                "Assign agents",
                options=list(agent_options.keys()),
                format_func=lambda aid: agent_options.get(aid, aid),
                default=[available_agents[0].agent_id] if available_agents else [],
                key="dp_agents",
            )

            issue_btn = st.button(
                "🚀 Issue Directive & Run",
                type="primary",
                use_container_width=True,
                key="dp_issue_btn",
                disabled=not (directive_title.strip() and selected_agent_ids),
            )

        with col_help:
            st.markdown("**Directive types**")
            for dtype in DirectiveType.ALL:
                colour = _DTYPE_COLOUR.get(dtype, "gray")
                st.markdown(f":{colour}[{DirectiveType.label(dtype)}]")
            st.caption(
                "Choose the type that best describes the goal. "
                "Agents will tailor their collaboration strategy accordingly."
            )

        if issue_btn and directive_title.strip() and selected_agent_ids:
            directive = platform.issue_directive(
                title=directive_title.strip(),
                description=directive_desc.strip() or directive_title.strip(),
                directive_type=directive_type,
                agent_ids=selected_agent_ids,
                human_author=human_author.strip() or "Operator",
            )

            st.success(f"✅ Directive `{directive.directive_id}` issued.")
            st.markdown("---")
            st.subheader("🔄 Live Collaboration Session")

            # Stream messages as they are produced
            session_container = st.container()
            progress_bar = st.progress(0.0, text="Starting…")

            assigned_agents = [
                a for aid in directive.assigned_agent_ids
                if (a := platform.registry.get(aid)) is not None
            ]
            # Estimate total messages: 1 opening + (1+insights+1) per agent + 1 closing
            # Insights ≈ 4 per agent; handoff/result = 1
            msgs_per_agent = 1 + 4 + 1
            est_total = 1 + len(assigned_agents) * msgs_per_agent + 1
            msg_count = 0

            with session_container:
                for msg, _ in platform.run_directive_streaming(directive.directive_id):
                    msg_count += 1
                    progress_bar.progress(
                        min(msg_count / est_total, 0.99),
                        text=f"[{msg.sender_name}] {MessageType.__dict__.get(msg.message_type.upper(), msg.message_type)}",
                    )
                    emoji = _MTYPE_EMOJI.get(msg.message_type, "•")
                    is_human = msg.sender_id == "human"
                    is_platform = msg.sender_id == "platform"
                    if is_human:
                        st.chat_message("user").markdown(msg.content)
                    elif is_platform:
                        with st.chat_message("assistant", avatar="🏛"):
                            st.markdown(f"**{msg.sender_name}:** {msg.content}")
                    else:
                        with st.chat_message("assistant", avatar="🤖"):
                            st.markdown(
                                f"{emoji} **{msg.sender_name}** _{msg.message_type}_\n\n"
                                f"{msg.content}"
                            )

            progress_bar.progress(1.0, text="✅ Session complete")
            st.balloons()
            st.rerun()

    # =========== Tab: Directives ============================================
    with tab_directives:
        st.subheader("All Directives")
        directives = platform.directives.list_all()

        if not directives:
            st.info(
                "No directives yet. Go to **➕ New Directive** to issue the first one."
            )
        else:
            # Filter controls
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                filter_status = st.selectbox(
                    "Filter by status",
                    options=["all"] + DirectiveStatus.ALL,
                    format_func=lambda s: "All statuses" if s == "all" else DirectiveStatus.label(s),
                    key="dp_filter_status",
                )
            with col_f2:
                filter_type = st.selectbox(
                    "Filter by type",
                    options=["all"] + DirectiveType.ALL,
                    format_func=lambda t: "All types" if t == "all" else DirectiveType.label(t),
                    key="dp_filter_type",
                )

            filtered = [
                d for d in directives
                if (filter_status == "all" or d.status == filter_status)
                and (filter_type == "all" or d.directive_type == filter_type)
            ]

            st.markdown(f"**{len(filtered)} directive(s) shown.**")
            for d in filtered:
                with st.container(border=True):
                    col_d1, col_d2 = st.columns([3, 1])
                    with col_d1:
                        st.markdown(f"**{d.title}** `{d.directive_id}`")
                        st.markdown(_directive_badge(d.directive_type, d.status))
                        if d.description and d.description != d.title:
                            st.caption(d.description[:200] + ("…" if len(d.description) > 200 else ""))
                    with col_d2:
                        st.caption(f"By: {d.human_author}")
                        import datetime as _dt
                        ts = _dt.datetime.fromtimestamp(d.created_at).strftime("%Y-%m-%d %H:%M")
                        st.caption(f"Created: {ts}")
                        if d.results:
                            st.caption(f"Results: {len(d.results)}")

                    # Expandable results
                    if d.results:
                        with st.expander("View results", expanded=False):
                            for r in d.results:
                                sid = r.get("session_id", "?")
                                agents = ", ".join(r.get("agents", []))
                                msgs = r.get("messages", 0)
                                st.markdown(
                                    f"Session `{sid}` — {agents} — {msgs} messages"
                                )

    # =========== Tab: Agents ================================================
    with tab_agents:
        st.subheader("Registered Agents")
        agents = platform.registry.list_all()

        if not agents:
            st.info("No agents registered.")
        else:
            st.markdown(f"**{len(agents)} agent(s) on the platform.**")
            agent_cols = st.columns(2)
            for i, agent in enumerate(agents):
                with agent_cols[i % 2]:
                    with st.container(border=True):
                        status_colour = {
                            AgentStatus.IDLE: "green",
                            AgentStatus.ACTIVE: "blue",
                            AgentStatus.UNAVAILABLE: "gray",
                        }.get(agent.status, "gray")
                        st.markdown(
                            f"### {agent.name} "
                            f":{status_colour}[{AgentStatus.label(agent.status)}]"
                        )
                        st.markdown(agent.description)
                        caps = " &nbsp;".join(
                            f"`{c}`" for c in agent.capabilities
                        )
                        st.markdown(f"**Capabilities:** {caps}", unsafe_allow_html=True)
                        if agent.current_directive_id:
                            st.caption(f"Working on directive: {agent.current_directive_id}")

    # =========== Tab: Sessions ==============================================
    with tab_sessions:
        st.subheader("Collaboration Sessions")
        sessions = platform.sessions.list_sessions()

        if not sessions:
            st.info("No collaboration sessions yet.")
        else:
            st.markdown(f"**{len(sessions)} session(s) on record.**")
            selected_session_id = st.selectbox(
                "Select a session to inspect",
                options=[s.session_id for s in sessions],
                format_func=lambda sid: (
                    f"{sid} — directive {next((s.directive_id for s in sessions if s.session_id == sid), '?')}"
                    f" — {next((s.status for s in sessions if s.session_id == sid), '?')}"
                ),
                key="dp_session_select",
            )

            session = platform.sessions.get_session(selected_session_id)
            if session:
                directive = platform.directives.get(session.directive_id)
                col_s1, col_s2, col_s3 = st.columns(3)
                with col_s1:
                    st.metric("Messages", len(session.messages))
                with col_s2:
                    st.metric("Participants", len(session.participant_ids))
                with col_s3:
                    duration = (
                        (session.ended_at or time.time()) - session.started_at
                    )
                    st.metric("Duration", f"{duration:.1f}s")

                if directive:
                    st.markdown(
                        f"**Directive:** {directive.title} "
                        + _directive_badge(directive.directive_type, directive.status)
                    )

                st.markdown("---")
                st.markdown("**Message Log**")
                for msg in session.messages:
                    emoji = _MTYPE_EMOJI.get(msg.message_type, "•")
                    is_human = msg.sender_id == "human"
                    is_platform = msg.sender_id == "platform"
                    if is_human:
                        st.chat_message("user").markdown(msg.content)
                    elif is_platform:
                        with st.chat_message("assistant", avatar="🏛"):
                            st.markdown(f"**{msg.sender_name}:** {msg.content}")
                    else:
                        with st.chat_message("assistant", avatar="🤖"):
                            st.markdown(
                                f"{emoji} **{msg.sender_name}** _{msg.message_type}_\n\n"
                                f"{msg.content}"
                            )


# ===========================================================================
# Navigation
# ===========================================================================

PAGES = {
    "🏠 Home": page_home,
    "🎬 Stupid Sindy Video Studio": page_sindy_studio,
    "🔬 Apex Lattice Analysis": page_apex_lattice,
    "🤝 AI Directive Platform": page_directive_platform,
}


def main() -> None:
    with st.sidebar:
        st.title("Barrot Agent")
        st.markdown("---")
        page_name = st.radio("Navigate to", list(PAGES.keys()), label_visibility="collapsed")

    PAGES[page_name]()


if __name__ == "__main__":
    main()
