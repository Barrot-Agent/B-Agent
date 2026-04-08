"""
Barrot Agent – Streamlit Application
======================================
Main entry point.  Provides a tabbed interface with:
  • Home – agent status / torch diagnostic
  • Stupid Sindy Video Studio – 15-episode video production pipeline
  • MCP Workflow – Hugging Face / Databricks / GitHub MCP integration
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

            if not run_btn:
                pass  # Already rendered above
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


# ===========================================================================
# Navigation
# ===========================================================================

PAGES = {
    "🏠 Home": page_home,
    "🎬 Stupid Sindy Video Studio": page_sindy_studio,
    "🔗 MCP Workflow": page_mcp_workflow,
}


def main() -> None:
    with st.sidebar:
        st.title("Barrot Agent")
        st.markdown("---")
        page_name = st.radio("Navigate to", list(PAGES.keys()), label_visibility="collapsed")

    PAGES[page_name]()


if __name__ == "__main__":
    main()
