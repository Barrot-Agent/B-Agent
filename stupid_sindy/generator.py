"""
Script generator and formatter for Stupid Sindy episodes.

Provides two output formats:
  - Plain-text screenplay format (readable / performable)
  - Markdown format (for documentation / GitHub rendering)
"""

from __future__ import annotations

from typing import Literal

from .episodes import EPISODES, get_episode, get_act, episode_count
from .characters import SINDY, ALL_CHARACTERS

OutputFormat = Literal["text", "markdown"]

ACT_TITLES = {
    1: "ACT ONE — COMEDY SKITS",
    2: "ACT TWO — THE VIBE CODE DISCOVERY",
    3: "ACT THREE — THE TRANSFORMATION & INVASION",
}

ACT_DESCRIPTIONS = {
    1: (
        "Sindy navigates everyday situations with brutal sarcasm "
        "and hidden genius. The world has no idea what it's dealing with."
    ),
    2: (
        "Sindy discovers Vibe Code: a resonant encoding architecture "
        "buried in non-coding DNA — a biological operating system "
        "that can rewrite what a living thing fundamentally *is*. "
        "She tests it. On herself."
    ),
    3: (
        "Sindy's modifications have changed her into something new. "
        "An alien fleet arrives to assess Earth for resource acquisition. "
        "They did not account for Sindy. "
        "Nobody ever does."
    ),
}


# ── Formatters ────────────────────────────────────────────────────────────────

def _format_beat_text(beat: dict) -> str:
    """Format a single beat as plain text."""
    if beat["type"] == "dialogue":
        return f"{beat['character'].upper().replace('_', ' ')}\n  {beat['line']}"
    else:
        return f"  [{beat['text']}]"


def _format_beat_markdown(beat: dict) -> str:
    """Format a single beat as markdown."""
    if beat["type"] == "dialogue":
        char = beat["character"].replace("_", " ").upper()
        return f"**{char}**\n> {beat['line']}"
    else:
        return f"*{beat['text']}*"


def _format_scene_text(scene: dict) -> str:
    """Format a single scene as plain text screenplay."""
    lines = [
        scene["heading"],
        "",
        scene["direction"],
        "",
    ]
    for beat in scene["beats"]:
        lines.append(_format_beat_text(beat))
        lines.append("")
    return "\n".join(lines)


def _format_scene_markdown(scene: dict) -> str:
    """Format a single scene as markdown."""
    lines = [
        f"### {scene['heading']}",
        "",
        f"_{scene['direction']}_",
        "",
    ]
    for beat in scene["beats"]:
        lines.append(_format_beat_markdown(beat))
        lines.append("")
    return "\n".join(lines)


def format_episode(episode: dict, fmt: OutputFormat = "text") -> str:
    """
    Render a full episode script in the requested format.

    Parameters
    ----------
    episode : dict
        An episode dict from episodes.EPISODES.
    fmt : OutputFormat
        Output format; 'text' or 'markdown'.

    Returns
    -------
    str
        The formatted script.
    """
    act_label = ACT_TITLES.get(episode["act"], f"ACT {episode['act']}")

    if fmt == "markdown":
        header = (
            f"# Episode {episode['number']}: {episode['title']}\n\n"
            f"**{act_label}**\n\n"
            f"**Tone:** {episode['tone']}\n\n"
            f"**Logline:** {episode['logline']}\n\n"
            f"---\n"
        )
        scenes_text = "\n---\n\n".join(
            _format_scene_markdown(s) for s in episode["scenes"]
        )
        return header + "\n" + scenes_text

    else:  # plain text
        divider = "=" * 72
        thin = "-" * 72
        header = (
            f"{divider}\n"
            f"EPISODE {episode['number']}: {episode['title'].upper()}\n"
            f"{act_label}\n"
            f"{thin}\n"
            f"TONE: {episode['tone']}\n"
            f"{thin}\n"
            f"LOGLINE: {episode['logline']}\n"
            f"{divider}\n"
        )
        scenes_text = ("\n" + thin + "\n\n").join(
            _format_scene_text(s) for s in episode["scenes"]
        )
        return header + "\n" + scenes_text


def format_series_overview(fmt: OutputFormat = "text") -> str:
    """
    Return a high-level overview of the full series.

    Parameters
    ----------
    fmt : OutputFormat
        Output format; 'text' or 'markdown'.

    Returns
    -------
    str
        The formatted overview.
    """
    if fmt == "markdown":
        lines = [
            "# STUPID SINDY — Series Overview",
            "",
            "> *A sarcastic genius, a biological revolution, and an alien invasion.*",
            "> *In that order. Mostly.*",
            "",
            "---",
            "",
        ]
        for act_num, title in ACT_TITLES.items():
            lines.append(f"## {title}")
            lines.append("")
            lines.append(ACT_DESCRIPTIONS[act_num])
            lines.append("")
            act_eps = get_act(act_num)
            for ep in act_eps:
                lines.append(
                    f"- **Episode {ep['number']}: {ep['title']}** — {ep['logline']}"
                )
            lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("## Main Characters")
        lines.append("")
        for char in ALL_CHARACTERS:
            lines.append(f"### {char.title} ({char.name})")
            lines.append("")
            lines.append(char.description)
            lines.append("")
            lines.append(f"**Arc:** {char.arc_note}")
            lines.append("")
            lines.append("**Catchphrases:**")
            for cp in char.catchphrases:
                lines.append(f'- *"{cp}"*')
            lines.append("")
        return "\n".join(lines)

    else:
        divider = "=" * 72
        thin = "-" * 72
        lines = [
            divider,
            "STUPID SINDY — SERIES OVERVIEW",
            divider,
            "",
            "  A sarcastic genius, a biological revolution, and an alien invasion.",
            "  In that order. Mostly.",
            "",
        ]
        for act_num, title in ACT_TITLES.items():
            lines.append(thin)
            lines.append(title)
            lines.append(thin)
            lines.append("")
            lines.append(ACT_DESCRIPTIONS[act_num])
            lines.append("")
            for ep in get_act(act_num):
                lines.append(
                    f"  Ep {ep['number']:>2}: {ep['title']:<35}  {ep['tone']}"
                )
            lines.append("")
        lines.append(thin)
        lines.append("MAIN CHARACTERS")
        lines.append(thin)
        for char in ALL_CHARACTERS:
            lines.append(f"\n{char.title.upper()} ({char.name})")
            lines.append(char.description)
            lines.append(f"Arc: {char.arc_note}")
        return "\n".join(lines)


def generate_episode(number: int, fmt: OutputFormat = "text") -> str:
    """
    Generate a formatted script for a single episode.

    Parameters
    ----------
    number : int
        Episode number (1-based).
    fmt : OutputFormat
        Output format; 'text' or 'markdown'.

    Returns
    -------
    str
        The formatted script.

    Raises
    ------
    ValueError
        If the episode number does not exist.
    """
    return format_episode(get_episode(number), fmt=fmt)


def generate_act(act_number: int, fmt: OutputFormat = "text") -> str:
    """
    Generate scripts for all episodes in a given act.

    Parameters
    ----------
    act_number : int
        Act number (1, 2, or 3).
    fmt : OutputFormat
        Output format; 'text' or 'markdown'.

    Returns
    -------
    str
        All episode scripts in the act, concatenated.
    """
    episodes = get_act(act_number)
    if not episodes:
        raise ValueError(f"Act {act_number} not found or has no episodes.")
    separator = "\n\n" + ("=" * 72) + "\n\n"
    return separator.join(format_episode(ep, fmt=fmt) for ep in episodes)


def generate_full_series(fmt: OutputFormat = "text") -> str:
    """
    Generate the complete series: overview + all episode scripts.

    Parameters
    ----------
    fmt : OutputFormat
        Output format; 'text' or 'markdown'.

    Returns
    -------
    str
        The complete series document.
    """
    separator = "\n\n" + ("=" * 72) + "\n\n"
    parts = [format_series_overview(fmt=fmt)]
    for ep in EPISODES:
        parts.append(format_episode(ep, fmt=fmt))
    return separator.join(parts)
