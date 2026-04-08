"""
Barrot Agent — AI-powered assistant with real-time 3D rendering capability.

This package provides the core agent logic as well as the comprehensive
dataset absorption system that enables Barrot to load, process, and render
assets from 40+ major global 3D datasets.
"""

__version__ = "2.0.0"
__author__ = "Barrot-Agent"

from barrot_agent.rendering import DatasetManager, AssetLoader, DatasetAnalytics

__all__ = [
    "DatasetManager",
    "AssetLoader",
    "DatasetAnalytics",
]
