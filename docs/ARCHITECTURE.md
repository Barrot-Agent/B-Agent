# Architecture

## Overview

B-Agent is a modular Python application integrating IBM Granite 4.0-3B Vision for multimodal AI tasks.

```
┌─────────────────────────────────────┐
│            Streamlit UI (app.py)    │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│          BAgent (core.py)           │
│   - Orchestrates components         │
│   - Configuration management        │
└──────┬──────────────────┬───────────┘
       │                  │
┌──────▼──────┐  ┌────────▼──────────┐
│ModelManager │  │ InferencePipeline │
│(models.py)  │  │ (inference.py)    │
└──────┬──────┘  └────────┬──────────┘
       │                  │
┌──────▼──────────────────▼──────────┐
│   IBM Granite 4.0-3B Vision        │
│   (Hugging Face Transformers)      │
└────────────────────────────────────┘
```

## Components

| Module | Purpose |
|---|---|
| `barrot_agent/core.py` | Main application orchestration |
| `barrot_agent/models.py` | Model lifecycle management |
| `barrot_agent/inference.py` | Inference pipeline |
| `barrot_agent/config.py` | Pydantic configuration |
| `barrot_agent/logger.py` | Structured logging |
| `app.py` | Streamlit web interface |

## Configuration Flow

Environment variables → `.env` file → Pydantic `AppConfig` → application components.

## Logging

Structured logging is available in JSON format (production) or human-readable format (development).
Log files are written to `logs/` with rotation at 10MB.
