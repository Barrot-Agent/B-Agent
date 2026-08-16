# API Reference

## barrot_agent.core.BAgent

Main application class.

### `__init__(config=None)`
Initialize with optional `AppConfig`. Defaults to environment-based config.

### `get_version() -> str`
Returns application version string.

### `get_model_id() -> str`
Returns the configured Hugging Face model identifier.

### `is_debug() -> bool`
Returns whether debug mode is enabled.

---

## directive_platform.SessionManager

### `import_transcript(source, source_kind="external", directive_id="imported")`

Import an explicitly selected local JSON, JSONL, Markdown, or text transcript
into a new persisted session. Imports are bounded to 5 MiB and retain source
provenance on every message; no network access or repository-wide scanning is
performed.

### `merge_sessions(session_ids, directive_id=None, participant_ids=None)`

Create a new chronological, de-duplicated session from existing session IDs.
Source sessions remain unchanged, and merged messages retain their origin in
`source_session_id` and `source_kind`.

---

## barrot_agent.models.ModelManager

Manages IBM Granite model lifecycle.

### `__init__(config=None)`
Initialize with optional `ModelConfig`.

### `is_loaded -> bool`
Property: returns True if model is loaded in memory.

### `load()`
Downloads and loads the model. Respects `load_in_8bit`, `load_in_4bit`, `tensor_type`.

### `unload()`
Frees model from memory.

### `get_metadata() -> dict`
Returns a copy of IBM Granite 4.0-3B Vision metadata (model ID, parameters, license, tags, ArXiv papers).

---

## barrot_agent.inference.InferencePipeline

### `__init__(model_manager)`
Initialize with a `ModelManager` instance.

### `run(prompt, image=None, max_new_tokens=512) -> str`
Run single inference. Accepts text prompt and optional PIL image.

### `run_batch(prompts, images=None, max_new_tokens=512) -> list[str]`
Run inference on a list of prompts.

---

## barrot_agent.config.AppConfig

Pydantic settings model. All fields are configurable via environment variables.

| Field | Env Var | Default |
|---|---|---|
| `environment` | `ENVIRONMENT` | `development` |
| `debug` | `DEBUG` | `false` |
| `hf_token` | `HF_TOKEN` | `None` |
| `log_level` | `LOG_LEVEL` | `INFO` |
| `model.model_id` | `MODEL__MODEL_ID` | `ibm-granite/granite-4.0-3b-vision` |
