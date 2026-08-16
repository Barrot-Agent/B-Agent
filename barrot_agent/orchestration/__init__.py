"""
barrot_agent.orchestration — pipeline orchestration, MCP coordination, and service bridges.

Modules
-------
mcp_orchestrator        Coordinates HF, Databricks, and GitHub MCP clients.
orchestrator_bridge     Bridge between the agent runtime and external orchestrators.
sync_manager            State synchronization manager across agent sessions.
mcp_databricks          Databricks MCP client integration.
mcp_github              GitHub MCP client integration.
mcp_huggingface         Hugging Face MCP client integration.
inference_node          Inference node registry and management.
inference_provider      Inference provider abstraction layer.
barrot_integration      Top-level Barrot integration entry point.
"""
