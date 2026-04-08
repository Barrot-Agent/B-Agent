"""
Barrot Agent – Streamlit Application
======================================
Main entry point.  Provides a tabbed interface with:
  • Home – agent status / torch diagnostic
  • Stupid Sindy Video Studio – 15-episode video production pipeline
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
# Navigation
# ===========================================================================

PAGES = {
    "🏠 Home": page_home,
    "🎬 Stupid Sindy Video Studio": page_sindy_studio,
    "🔬 Apex Lattice Analysis": page_apex_lattice,
}


def main() -> None:
    with st.sidebar:
        st.title("Barrot Agent")
        st.markdown("---")
        page_name = st.radio("Navigate to", list(PAGES.keys()), label_visibility="collapsed")

    PAGES[page_name]()


if __name__ == "__main__":
    main()
