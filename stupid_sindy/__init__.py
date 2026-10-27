"""
Stupid Sindy — Episodic Comedy Skit Series Generator

A serialised comedy/sci-fi series featuring Sindy: a sarcastic, brilliant
character who navigates everyday absurdity before discovering Vibe Code
and becoming humanity's deadpan protector against an alien invasion.

Public API
----------
    from stupid_sindy import generate_episode, generate_act, generate_full_series
    from stupid_sindy import format_series_overview
    from stupid_sindy.characters import SINDY, ALL_CHARACTERS
    from stupid_sindy.episodes import EPISODES, get_episode, get_act

CLI
---
    python -m stupid_sindy --help
"""

from .generator import (
    generate_episode,
    generate_act,
    generate_full_series,
    format_series_overview,
)
from .episodes import EPISODES, get_episode, get_act, episode_count
from .characters import SINDY, ALL_CHARACTERS, get_character

__all__ = [
    "generate_episode",
    "generate_act",
    "generate_full_series",
    "format_series_overview",
    "EPISODES",
    "get_episode",
    "get_act",
    "episode_count",
    "SINDY",
    "ALL_CHARACTERS",
    "get_character",
]
