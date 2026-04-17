"""
Barrot Agent – Streamlit Application
======================================
Main entry point.  Provides a tabbed interface with:
  • Home – agent status / torch diagnostic
  • Stupid Sindy Video Studio – 15-episode video production pipeline
  • MCP Workflow – Hugging Face / Databricks / GitHub MCP integration
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
from mcp_orchestrator import (  # noqa: E402
    MCPOrchestrator,
    OrchestratorConfig,
    OrchestratorStep,
)
from barrot_agent import (  # noqa: E402
    SmartAgent,
    AgentEventType,
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
        st.info("Navigate to **🤖 Smart Agent** in the sidebar to give Barrot a goal.")

    st.divider()
    st.markdown(
        """
### About Barrot Agent
Barrot is a self-improving agent infrastructure that combines:
- **Autonomous task execution** via the Smart Agent (plan → act → observe loop)
- **Multi-agent collaboration** via the AI Directive Platform
- **Sandbox analysis** via the Apex Lattice cascade system
- **Creative video production** via the Stupid Sindy pipeline
- **Distributed inference** and MCP workflow integration

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
# Page: MCP Workflow
# ===========================================================================

_MCP_STEP_EMOJI = {
    OrchestratorStep.INIT:               "🚀",
    OrchestratorStep.HF_MODELS:          "🤗",
    OrchestratorStep.SCRIPT_GEN:         "📝",
    OrchestratorStep.DATABRICKS_SUBMIT:  "☁️",
    OrchestratorStep.DATABRICKS_WAIT:    "⏳",
    OrchestratorStep.LOCAL_RENDER:       "🎬",
    OrchestratorStep.GITHUB_COMMIT:      "📤",
    OrchestratorStep.CICD_TRIGGER:       "⚙️",
    OrchestratorStep.COMPLETE:           "✅",
    OrchestratorStep.ERROR:              "❌",
}


def _mcp_config_from_ui(
    hf_token: str,
    db_host: str,
    db_token: str,
    db_cluster: str,
    gh_token: str,
    download_models: bool,
    use_databricks: bool,
    commit_to_github: bool,
    trigger_cicd: bool,
) -> OrchestratorConfig:
    return OrchestratorConfig(
        hf_token=hf_token or None,
        databricks_host=db_host or None,
        databricks_token=db_token or None,
        databricks_cluster_id=db_cluster or None,
        github_token=gh_token or None,
        download_models=download_models,
        use_databricks=use_databricks,
        commit_to_github=commit_to_github,
        trigger_cicd=trigger_cicd,
    )


def page_mcp_workflow() -> None:
    st.title("🔗 MCP Workflow")
    st.markdown(
        "Integrate Hugging Face, Databricks, and GitHub MCP services into the "
        "Stupid Sindy video generation pipeline."
    )

    # -----------------------------------------------------------------------
    # Configuration sidebar
    # -----------------------------------------------------------------------
    with st.sidebar:
        st.header("🔑 MCP Configuration")

        with st.expander("🤗 Hugging Face", expanded=False):
            hf_token = st.text_input(
                "HF Token",
                type="password",
                key="mcp_hf_token",
                help="Hugging Face API token (hf_…)",
            )

        with st.expander("☁️ Databricks", expanded=False):
            db_host = st.text_input(
                "Workspace Host",
                key="mcp_db_host",
                placeholder="https://adb-123456.azuredatabricks.net",
            )
            db_token = st.text_input(
                "Access Token",
                type="password",
                key="mcp_db_token",
                help="Databricks personal access token (dapi…)",
            )
            db_cluster = st.text_input(
                "Cluster ID (optional)",
                key="mcp_db_cluster",
                placeholder="0123-456789-abc12345",
            )

        with st.expander("📦 GitHub", expanded=False):
            gh_token = st.text_input(
                "Personal Access Token",
                type="password",
                key="mcp_gh_token",
                help="GitHub PAT with repo + workflow scopes",
            )

        st.divider()
        st.markdown("**Pipeline Options**")
        download_models = st.toggle("Download HF Models", value=True, key="mcp_dl_models")
        use_databricks = st.toggle("Use Databricks Compute", value=True, key="mcp_use_db")
        commit_to_github = st.toggle("Commit to GitHub", value=True, key="mcp_commit_gh")
        trigger_cicd = st.toggle("Trigger CI/CD", value=True, key="mcp_trigger_cicd")

        st.divider()
        mcp_ep = st.selectbox(
            "Select Episode",
            options=list(range(1, 16)),
            format_func=lambda n: f"Ep {n}: {get_episode(n).title}",
            key="mcp_selected_ep",
        )
        run_btn = st.button("▶ Run MCP Workflow", use_container_width=True, type="primary")

    # -----------------------------------------------------------------------
    # Main content
    # -----------------------------------------------------------------------
    tab_status, tab_config, tab_history = st.tabs(
        ["📊 Status", "⚙️ Config Check", "📜 Run History"]
    )

    # == Tab 1: Status / run ==
    with tab_status:
        st.subheader(f"Episode {mcp_ep}: {get_episode(mcp_ep).title}")

        if run_btn:
            cfg = _mcp_config_from_ui(
                hf_token=st.session_state.get("mcp_hf_token", ""),
                db_host=st.session_state.get("mcp_db_host", ""),
                db_token=st.session_state.get("mcp_db_token", ""),
                db_cluster=st.session_state.get("mcp_db_cluster", ""),
                gh_token=st.session_state.get("mcp_gh_token", ""),
                download_models=st.session_state.get("mcp_dl_models", True),
                use_databricks=st.session_state.get("mcp_use_db", True),
                commit_to_github=st.session_state.get("mcp_commit_gh", True),
                trigger_cicd=st.session_state.get("mcp_trigger_cicd", True),
            )
            orch = MCPOrchestrator(cfg)

            progress_bar = st.progress(0.0, text="Initialising MCP workflow…")
            log_container = st.container()
            log_lines = []

            for event in orch.run_episode(mcp_ep):
                emoji = _MCP_STEP_EMOJI.get(event.step, "•")
                progress_bar.progress(
                    event.progress,
                    text=f"{emoji} {event.message}",
                )
                colour = "red" if event.is_error else ("green" if event.is_complete else "blue")
                log_lines.append(
                    f":{colour}[{emoji} **{event.step.value.upper()}**] {event.message}"
                )
                with log_container:
                    for line in log_lines:
                        st.markdown(line)

                if event.is_error:
                    st.error(f"Pipeline error: {event.error}")
                    break

        else:
            st.info(
                "Configure credentials in the sidebar, select an episode, "
                "and click **▶ Run MCP Workflow** to start."
            )

    # == Tab 2: Config check ==
    with tab_config:
        st.subheader("Service Configuration Status")
        cfg_check = OrchestratorConfig(
            hf_token=st.session_state.get("mcp_hf_token") or None,
            databricks_host=st.session_state.get("mcp_db_host") or None,
            databricks_token=st.session_state.get("mcp_db_token") or None,
            github_token=st.session_state.get("mcp_gh_token") or None,
        )
        check_results = MCPOrchestrator(cfg_check).validate_config()

        col_hf, col_db, col_gh = st.columns(3)
        with col_hf:
            with st.container(border=True):
                st.markdown("### 🤗 Hugging Face")
                if check_results["huggingface"]:
                    st.success("Token configured")
                else:
                    st.warning("Token missing")
                st.caption("Used for model downloads")

        with col_db:
            with st.container(border=True):
                st.markdown("### ☁️ Databricks")
                if check_results["databricks"]:
                    st.success("Host + Token configured")
                else:
                    st.warning("Host or Token missing")
                st.caption("Used for remote rendering")

        with col_gh:
            with st.container(border=True):
                st.markdown("### 📦 GitHub")
                if check_results["github"]:
                    st.success("Token configured")
                else:
                    st.warning("Token missing")
                st.caption("Used for auto-commit + CI/CD")

        st.divider()
        st.markdown(
            "ℹ️ You can also set credentials via environment variables: "
            "`HF_TOKEN`, `DATABRICKS_HOST`, `DATABRICKS_TOKEN`, `GITHUB_TOKEN`."
        )

    # == Tab 3: Run history ==
    with tab_history:
        st.subheader("MCP Run History (this session)")
        # Show a placeholder – history is per-orchestrator instance
        st.info(
            "Run history is tracked per session.  "
            "Start a workflow above to see entries here."
        )
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
# Page: Research
# ===========================================================================

# Curated research source registry (subset of issue #178 sources)
_RESEARCH_SOURCES: dict[str, list[dict[str, str]]] = {
    "Academic & Preprints": [
        {"name": "arXiv", "url": "https://arxiv.org", "focus": "CS, Physics, Math, AI/ML preprints"},
        {"name": "bioRxiv", "url": "https://biorxiv.org", "focus": "Biology preprints"},
        {"name": "PubMed", "url": "https://pubmed.ncbi.nlm.nih.gov", "focus": "Biomedical literature"},
        {"name": "Papers With Code", "url": "https://paperswithcode.com", "focus": "ML papers + implementations"},
        {"name": "Semantic Scholar", "url": "https://semanticscholar.org", "focus": "AI-powered research search"},
    ],
    "AI Labs & Blogs": [
        {"name": "OpenAI Blog", "url": "https://openai.com/blog", "focus": "GPT, alignment, safety"},
        {"name": "DeepMind Research", "url": "https://deepmind.google/research", "focus": "RL, AlphaFold, Gemini"},
        {"name": "Anthropic Research", "url": "https://anthropic.com/research", "focus": "Constitutional AI, safety"},
        {"name": "Meta AI Research", "url": "https://ai.meta.com/research", "focus": "LLaMA, FAIR research"},
        {"name": "Google AI Blog", "url": "https://ai.googleblog.com", "focus": "Google AI/ML advances"},
    ],
    "Datasets & Benchmarks": [
        {"name": "Hugging Face", "url": "https://huggingface.co", "focus": "Models, datasets, spaces"},
        {"name": "Kaggle", "url": "https://kaggle.com", "focus": "Competitions and datasets"},
        {"name": "UCI ML Repository", "url": "https://archive.ics.uci.edu", "focus": "Classic ML datasets"},
        {"name": "Google Dataset Search", "url": "https://datasetsearch.research.google.com", "focus": "Dataset discovery"},
        {"name": "ARC-AGI", "url": "https://arcprize.org", "focus": "AGI evaluation benchmark"},
    ],
    "Knowledge & Encyclopaedias": [
        {"name": "Wikipedia", "url": "https://en.wikipedia.org", "focus": "General encyclopaedia"},
        {"name": "Wikidata", "url": "https://wikidata.org", "focus": "Structured knowledge graph"},
        {"name": "Stanford Encyclopaedia of Philosophy", "url": "https://plato.stanford.edu", "focus": "Philosophy & ethics"},
        {"name": "ConceptNet", "url": "https://conceptnet.io", "focus": "Commonsense knowledge graph"},
        {"name": "Wolfram Alpha", "url": "https://wolframalpha.com", "focus": "Computational knowledge"},
    ],
    "News & Current Events": [
        {"name": "MIT Technology Review", "url": "https://technologyreview.com", "focus": "Emerging tech"},
        {"name": "Quanta Magazine", "url": "https://quantamagazine.org", "focus": "Math & science journalism"},
        {"name": "The Gradient", "url": "https://thegradient.pub", "focus": "ML research analysis"},
        {"name": "Import AI (Jack Clark)", "url": "https://importai.substack.com", "focus": "Weekly AI newsletter"},
        {"name": "Ars Technica", "url": "https://arstechnica.com", "focus": "Tech & science news"},
    ],
    "Code & Open-Source": [
        {"name": "GitHub", "url": "https://github.com", "focus": "Source code and projects"},
        {"name": "PyPI", "url": "https://pypi.org", "focus": "Python packages"},
        {"name": "TensorFlow Hub", "url": "https://tfhub.dev", "focus": "Pre-trained TF models"},
        {"name": "Weights & Biases", "url": "https://wandb.ai", "focus": "ML experiment tracking"},
        {"name": "Lightning AI", "url": "https://lightning.ai", "focus": "PyTorch Lightning & training"},
    ],
}

# Research methodologies practiced on the platform
_METHODOLOGIES: list[dict[str, str]] = [
    {
        "name": "Plan → Act → Observe (PAO) Loop",
        "description": (
            "The SmartAgent decomposes any goal into a typed plan, executes each "
            "step with a built-in tool, reflects on intermediate results, and "
            "converges on a consolidated answer. Enables autonomous, transparent "
            "task execution without an external LLM."
        ),
        "agent": "SmartAgent",
    },
    {
        "name": "Progressive Ping-Pong Protocol",
        "description": (
            "Multi-agent cascade where each specialist agent passes enriched "
            "findings to the next, building progressively deeper insight. "
            "Designed to leverage complementary capabilities across the council."
        ),
        "agent": "All council agents",
    },
    {
        "name": "Adversarial Stress-Testing (Red Team)",
        "description": (
            "HRM-X systematically challenges every conclusion by probing "
            "assumptions, injecting edge cases, and attempting to falsify "
            "results before they are accepted into the knowledge base."
        ),
        "agent": "HRM-X (Adversarial)",
    },
    {
        "name": "Temporal Causal Chain Analysis",
        "description": (
            "HRM-T traces causes backward through time and projects forward "
            "using predictive models, adding the time dimension to any "
            "structural analysis already performed by AnalystAgent."
        ),
        "agent": "HRM-T (Temporal)",
    },
    {
        "name": "Multi-Framework Ethics Review",
        "description": (
            "HRM-Phi applies consequentialist, deontological, and virtue-ethics "
            "lenses in parallel to evaluate every major conclusion, surfacing "
            "value misalignments before final delivery."
        ),
        "agent": "HRM-Phi (Ethics)",
    },
    {
        "name": "Emergence & Feedback Loop Mapping",
        "description": (
            "HRM-Sigma builds causal-loop diagrams of the system under analysis, "
            "identifies reinforcing and balancing feedback loops, and flags "
            "emergent properties that reductionist analysis would miss."
        ),
        "agent": "HRM-Sigma (Systems)",
    },
    {
        "name": "Cross-Source Corroboration",
        "description": (
            "CorroborationAgent and HRM-X cross-reference claims across "
            "independent sources to detect contradictions, surface consensus, "
            "and assign confidence scores to each piece of knowledge."
        ),
        "agent": "CorroborationAgent + HRM-X",
    },
    {
        "name": "Indigenous Wisdom Integration",
        "description": (
            "Wisdom-I enriches conclusions with long-term, nature-based, and "
            "culturally diverse perspectives drawn from global indigenous "
            "traditions, ensuring outputs resonate beyond Western frameworks."
        ),
        "agent": "Wisdom-I (Indigenous)",
    },
]


def page_research() -> None:
    st.title("📚 Research Section")
    st.markdown(
        "A living knowledge hub tracking discoveries, methodologies, ingestion "
        "sources, and the full agent council. Updated as the platform evolves."
    )

    tab_disc, tab_meth, tab_sources, tab_agents, tab_reasoning = st.tabs([
        "💡 Discoveries",
        "⚙️ Methodologies",
        "📡 Ingestion Sources",
        "🤖 Agent Council",
        "🧠 Reasoning Chains",
    ])

    # =========== Discoveries ================================================
    with tab_disc:
        st.subheader("Recent Discoveries & Breakthroughs")
        st.markdown(
            "Discoveries are generated when directives complete and agents "
            "surface novel insights. Run a directive on the **🤝 AI Directive "
            "Platform** page to populate this section."
        )

        # Load completed directive results as proxy discoveries
        platform = get_directive_platform()
        completed = [
            d for d in platform.directives.list_all()
            if d.status == "completed" and d.results
        ]

        if not completed:
            st.info(
                "No discoveries recorded yet. "
                "Complete a directive to generate findings."
            )
        else:
            st.markdown(f"**{len(completed)} directive(s) with results:**")
            for d in completed:
                with st.expander(f"💡 {d.title}", expanded=False):
                    st.markdown(f"**Type:** {d.directive_type}")
                    st.markdown(f"**Author:** {d.human_author}")
                    for r in d.results:
                        sid = r.get("session_id", "?")
                        agents = ", ".join(r.get("agents", []))
                        msgs = r.get("messages", 0)
                        st.markdown(
                            f"Session `{sid}` — agents: {agents} — {msgs} messages"
                        )

    # =========== Methodologies ==============================================
    with tab_meth:
        st.subheader("Research Methodologies")
        st.markdown(
            "Core processes and protocols employed by Barrot's agent council "
            "to generate reliable, multi-perspective research outputs."
        )
        for i, meth in enumerate(_METHODOLOGIES):
            with st.container(border=True):
                col_m1, col_m2 = st.columns([3, 1])
                with col_m1:
                    st.markdown(f"**{meth['name']}**")
                    st.markdown(meth["description"])
                with col_m2:
                    st.caption(f"Agent: {meth['agent']}")

    # =========== Ingestion Sources ==========================================
    with tab_sources:
        st.subheader("Ingestion Source Registry")
        st.markdown(
            "Curated list of high-quality sources used for knowledge ingestion, "
            "organized by category. Continuously expanded as gaps are detected."
        )

        search_q = st.text_input(
            "Filter sources",
            placeholder="e.g. AI, datasets, philosophy…",
            key="research_src_filter",
        )

        for category, sources in _RESEARCH_SOURCES.items():
            filtered_sources = [
                s for s in sources
                if not search_q or search_q.lower() in (
                    s["name"] + " " + s["focus"]
                ).lower()
            ]
            if not filtered_sources:
                continue
            with st.expander(f"📂 {category} ({len(filtered_sources)})", expanded=not search_q):
                for src in filtered_sources:
                    col_s1, col_s2 = st.columns([2, 3])
                    with col_s1:
                        st.markdown(f"**[{src['name']}]({src['url']})**")
                    with col_s2:
                        st.caption(src["focus"])

    # =========== Agent Council ==============================================
    with tab_agents:
        st.subheader("Agent Council Profiles")
        st.markdown(
            "All agents registered on the Directive Platform, grouped by tier. "
            "Click **🤝 AI Directive Platform** to assign directives."
        )

        platform = get_directive_platform()
        agents = platform.registry.list_all()

        # Group by rough tier using known prefixes / IDs
        tiers: dict[str, list] = {
            "Core": [],
            "HRM Council": [],
            "Extended HRM (Tier 2.5)": [],
            "Cultural & Wisdom": [],
            "Autonomous": [],
        }
        for ag in agents:
            aid = ag.agent_id
            if aid in ("barrot-agent", "project-agent"):
                tiers["Core"].append(ag)
            elif aid in ("learner-agent", "analyst-agent", "refinement-agent", "corroboration-agent"):
                tiers["HRM Council"].append(ag)
            elif aid.startswith("hrm-"):
                tiers["Extended HRM (Tier 2.5)"].append(ag)
            elif aid.startswith("wisdom-"):
                tiers["Cultural & Wisdom"].append(ag)
            else:
                tiers["Autonomous"].append(ag)

        for tier_name, tier_agents in tiers.items():
            if not tier_agents:
                continue
            st.markdown(f"#### {tier_name}")
            cols = st.columns(2)
            for idx, ag in enumerate(tier_agents):
                with cols[idx % 2]:
                    with st.container(border=True):
                        status_colour = {
                            "idle": "green",
                            "active": "blue",
                            "unavailable": "gray",
                        }.get(ag.status, "gray")
                        st.markdown(
                            f"**{ag.name}** "
                            f":{status_colour}[● {ag.status.upper()}]"
                        )
                        st.caption(ag.description[:160] + ("…" if len(ag.description) > 160 else ""))
                        caps = " &nbsp;".join(f"`{c}`" for c in ag.capabilities[:4])
                        st.markdown(caps, unsafe_allow_html=True)

    # =========== Reasoning Chains ===========================================
    with tab_reasoning:
        st.subheader("Transparent Reasoning Chains")
        st.markdown(
            "Reasoning chains are produced by the **🤖 Smart Agent** during "
            "plan-act-observe execution. Run the Smart Agent on a goal to "
            "generate transparent step-by-step reasoning here."
        )
        st.info(
            "Tip: Run the Smart Agent from the **🤖 Smart Agent** page, then "
            "return here to review the reasoning structure for each goal."
        )

        # Display reasoning guide
        with st.expander("📖 How Reasoning Chains Work", expanded=True):
            st.markdown(
                """
**Step 1 — THINKING:** The agent analyses the goal, identifies constraints,
and decides on a strategy before committing to a plan.

**Step 2 — PLAN:** A typed sequence of `PlanStep` objects is produced, each
specifying the tool to invoke and the expected output.

**Step 3 — ACTION + TOOL RESULT:** Each step calls a built-in tool
(`search`, `analyze`, `reason`, `code`, or `summarize`) and records the raw output.

**Step 4 — OBSERVATION:** After each tool call the agent reflects on the
result, adjusting its understanding before proceeding to the next step.

**Step 5 — ANSWER:** All observations are consolidated into a final,
coherent response that directly addresses the original goal.
                """
            )




_SMART_AGENT_EVENT_EMOJI: dict[AgentEventType, str] = {
    AgentEventType.GOAL:        "🎯",
    AgentEventType.THINKING:    "🧠",
    AgentEventType.PLAN:        "📋",
    AgentEventType.ACTION:      "⚡",
    AgentEventType.TOOL_RESULT: "🔧",
    AgentEventType.OBSERVATION: "👁",
    AgentEventType.ANSWER:      "✅",
    AgentEventType.ERROR:       "❌",
}

_SMART_AGENT_EVENT_COLOUR: dict[AgentEventType, str] = {
    AgentEventType.GOAL:        "blue",
    AgentEventType.THINKING:    "violet",
    AgentEventType.PLAN:        "orange",
    AgentEventType.ACTION:      "blue",
    AgentEventType.TOOL_RESULT: "gray",
    AgentEventType.OBSERVATION: "green",
    AgentEventType.ANSWER:      "green",
    AgentEventType.ERROR:       "red",
}


@st.cache_resource(show_spinner=False)
def get_smart_agent() -> SmartAgent:
    return SmartAgent()


def page_smart_agent() -> None:
    st.title("🤖 Smart Agent")
    st.markdown(
        "Give Barrot a goal and watch it **autonomously plan, act, and reason** its way "
        "to an answer — breaking work down step-by-step and using built-in tools."
    )

    # -----------------------------------------------------------------------
    # Sidebar: quick reference
    # -----------------------------------------------------------------------
    with st.sidebar:
        st.header("💡 Example Goals")
        example_goals = [
            "Research the latest advances in AI agents",
            "Explain how transformer attention mechanisms work",
            "Analyse the architecture of multi-agent systems",
            "Build a data processing pipeline for time-series forecasting",
            "Learn about reinforcement learning from human feedback",
            "Investigate the safety challenges in large language models",
        ]
        selected_example = st.selectbox(
            "Load an example",
            options=["(type your own below)"] + example_goals,
            key="sa_example",
        )
        st.divider()
        st.markdown("**How it works**")
        st.markdown(
            "1. 🧠 **Plan** — infer intent and build a step-by-step plan\n"
            "2. ⚡ **Act** — execute each step with a built-in tool\n"
            "3. 👁 **Observe** — reflect on each result\n"
            "4. ✅ **Answer** — consolidate everything into a final response"
        )
        st.divider()
        st.markdown("**Available tools**")
        for tool, desc in [
            ("`search`",    "Query the knowledge base"),
            ("`analyze`",   "Deep structural analysis"),
            ("`reason`",    "Structured reasoning chain"),
            ("`code`",      "Generate code scaffolds"),
            ("`summarize`", "Condense findings"),
        ]:
            st.markdown(f"- {tool} — {desc}")

    # -----------------------------------------------------------------------
    # Goal input
    # -----------------------------------------------------------------------
    default_goal = (
        selected_example
        if selected_example != "(type your own below)"
        else ""
    )
    goal = st.text_area(
        "Enter your goal",
        value=default_goal,
        placeholder="e.g. Research the latest advances in AI agents",
        height=80,
        key="sa_goal_input",
    )

    run_col, clear_col = st.columns([3, 1])
    with run_col:
        run_btn = st.button(
            "🚀 Run Smart Agent",
            type="primary",
            use_container_width=True,
            disabled=not goal.strip(),
        )
    with clear_col:
        clear_btn = st.button("🗑 Clear", use_container_width=True)
    if clear_btn:
        st.session_state.pop("sa_goal_input", None)
        st.rerun()

    # -----------------------------------------------------------------------
    # Agent execution
    # -----------------------------------------------------------------------
    if run_btn and goal.strip():
        agent = get_smart_agent()

        st.divider()
        st.subheader("🔄 Live Execution")

        # Count expected events to drive progress bar
        # goal + 4 thinking + plan + N*(action+tool_result+observation) + answer
        # N is at most 4 steps; use 18 as a reasonable upper bound
        _EST_TOTAL = 18
        progress = st.progress(0.0, text="Starting…")
        event_count = 0

        execution_container = st.container()

        with execution_container:
            for event in agent.run(goal.strip()):
                event_count += 1
                progress.progress(
                    min(event_count / _EST_TOTAL, 0.95),
                    text=f"{_SMART_AGENT_EVENT_EMOJI.get(event.type, '•')} "
                         f"{event.type.value.replace('_', ' ').title()}…",
                )

                emoji = _SMART_AGENT_EVENT_EMOJI.get(event.type, "•")
                colour = _SMART_AGENT_EVENT_COLOUR.get(event.type, "gray")
                label = event.type.value.replace("_", " ").title()

                if event.type == AgentEventType.GOAL:
                    st.info(f"{emoji} {event.content}")

                elif event.type == AgentEventType.THINKING:
                    st.markdown(f":{colour}[{emoji} *{event.content}*]")

                elif event.type == AgentEventType.PLAN:
                    with st.expander(f"{emoji} Execution Plan", expanded=True):
                        st.markdown(event.content)

                elif event.type == AgentEventType.ACTION:
                    with st.container(border=True):
                        st.markdown(f":{colour}[{emoji} **{label}**]")
                        st.markdown(event.content)

                elif event.type == AgentEventType.TOOL_RESULT:
                    with st.expander(f"{emoji} Tool Output", expanded=False):
                        st.markdown(event.content)

                elif event.type == AgentEventType.OBSERVATION:
                    st.markdown(f":{colour}[{emoji} {event.content}]")

                elif event.type == AgentEventType.ANSWER:
                    progress.progress(1.0, text="✅ Complete!")
                    st.divider()
                    st.subheader("✅ Final Answer")
                    st.markdown(event.content)
                    st.balloons()

                elif event.type == AgentEventType.ERROR:
                    progress.progress(1.0, text="❌ Error")
                    st.error(f"{emoji} {event.content}")
                    break

        if event_count > 0 and not run_btn:
            progress.progress(1.0, text="Done")


# ===========================================================================
# Navigation
# ===========================================================================

PAGES = {
    "🏠 Home": page_home,
    "🤖 Smart Agent": page_smart_agent,
    "📚 Research": page_research,
    "🎬 Stupid Sindy Video Studio": page_sindy_studio,
    "🔗 MCP Workflow": page_mcp_workflow,
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
